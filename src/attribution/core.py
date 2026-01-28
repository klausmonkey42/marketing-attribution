"""
Core attribution calculation engine.

Implements multi-touch attribution models with support for different
conversion types and credit allocation strategies.
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, Callable
from datetime import date
import logging

from attribution.models import (
    ConversionType, AttributionConfig, AttributionDataFrame
)
from attribution.matchers import CustomerMatcher
from utils.date import parse_date, is_before

logger = logging.getLogger(__name__)


class AttributionEngine:
    """
    Multi-touch attribution calculation engine.
    
    Calculates attribution credit for marketing touchpoints using configurable
    models and conversion definitions.
    """
    
    def __init__(self, config: Optional[AttributionConfig] = None):
        """
        Initialize attribution engine.
        
        Args:
            config: Attribution configuration (uses defaults if not provided)
        """
        self.config = config or AttributionConfig()
        logger.info(f"Initialized AttributionEngine with {self.config.conversion_type.value}")
    
    def calculate_attribution(self,
                            interactions_df: pd.DataFrame,
                            customers_df: pd.DataFrame,
                            revenue_df: Optional[pd.DataFrame] = None,
                            channel_mapping: Optional[Dict[str, str]] = None) -> AttributionDataFrame:
        """
        Calculate attribution for all customer touchpoints.
        
        Workflow:
        1. Match interactions to customers
        2. Determine conversion event per customer
        3. Filter touchpoints to pre-conversion only
        4. Calculate attribution credit share
        5. Attribute revenue (if provided)
        
        Args:
            interactions_df: Marketing interactions with columns:
                - id: Interaction ID
                - called_at: Timestamp
                - source/referral: Marketing source
                - contact_number/email: Contact info
            
            customers_df: Customer data with columns:
                - customer_id: Unique ID
                - phone_1, phone_2, etc.: Phone numbers
                - email_1, email_2: Email addresses
            
            revenue_df: Optional revenue data with columns:
                - customer_id: Customer ID
                - service_date: Date of service
                - net: Revenue amount
            
            channel_mapping: Optional dict mapping sources to channels
        
        Returns:
            AttributionDataFrame with calculated attribution
        """
        logger.info("Starting attribution calculation...")
        
        # Step 1: Match interactions to customers
        matcher = CustomerMatcher(customers_df)
        matched_interactions = matcher.match_all(interactions_df)
        
        if len(matched_interactions) == 0:
            logger.warning("No interactions matched to customers")
            return AttributionDataFrame(pd.DataFrame())
        
        match_stats = matcher.get_match_statistics(matched_interactions)
        logger.info(f"Matched {match_stats['total_matches']} interactions "
                   f"to {match_stats['unique_customers']} customers")
        
        # Step 2: Parse dates and map channels
        matched_interactions = self._prepare_interactions(
            matched_interactions, 
            channel_mapping
        )
        
        # Step 3: Determine conversion events
        conversion_dates = self._get_conversion_dates(
            customers_df,
            revenue_df
        )
        
        # Step 4: Filter to pre-conversion touchpoints
        attributed = self._filter_to_pre_conversion(
            matched_interactions,
            conversion_dates
        )
        
        if len(attributed) == 0:
            logger.warning("No pre-conversion touchpoints found")
            return AttributionDataFrame(pd.DataFrame())
        
        # Step 5: Calculate attribution credits
        attributed = self._calculate_credits(attributed)
        
        # Step 6: Attribute revenue (if provided)
        if revenue_df is not None:
            attributed = self._attribute_revenue(attributed, revenue_df, conversion_dates)
        
        logger.info(f"Attribution complete: {len(attributed)} touchpoints, "
                   f"{attributed['customer_id'].nunique()} customers")
        
        return AttributionDataFrame(attributed)
    
    def _prepare_interactions(self, 
                            interactions_df: pd.DataFrame,
                            channel_mapping: Optional[Dict[str, str]] = None) -> pd.DataFrame:
        """Prepare interactions: parse dates, map channels."""
        df = interactions_df.copy()
        
        # Parse interaction date
        date_col = 'called_at' if 'called_at' in df.columns else 'interaction_date'
        if date_col in df.columns:
            df['interaction_date'] = df[date_col].apply(
                lambda x: parse_date(str(x)[:10]) if pd.notna(x) else None
            )
        
        # Drop rows with invalid dates
        df = df[df['interaction_date'].notna()]
        
        # Map to channels
        if channel_mapping:
            source_col = 'source' if 'source' in df.columns else 'channel'
            if source_col in df.columns:
                df['channel'] = df[source_col].map(channel_mapping).fillna(df[source_col])
        elif 'channel' not in df.columns:
            # Use source as channel if no mapping provided
            df['channel'] = df.get('source', 'Unknown')
        
        # Fill any remaining nulls
        df['channel'] = df['channel'].fillna('Unknown')
        
        return df
    
    def _get_conversion_dates(self,
                            customers_df: pd.DataFrame,
                            revenue_df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """
        Get conversion date for each customer based on conversion type.
        
        Returns:
            DataFrame with customer_id and conversion_date
        """
        conversion_type = self.config.conversion_type
        
        if conversion_type == ConversionType.FIRST_CONTACT:
            # All customers convert on first contact (no filtering needed)
            return pd.DataFrame({
                'customer_id': customers_df['customer_id'],
                'conversion_date': pd.NaT
            })
        
        elif conversion_type == ConversionType.FIRST_PAID:
            # Get first paid date from revenue data
            if revenue_df is None:
                raise ValueError("revenue_df required for FIRST_PAID conversion type")
            
            revenue = revenue_df.copy()
            revenue['service_date'] = revenue['service_date'].apply(parse_date)
            revenue = revenue[revenue['service_date'].notna()]
            
            first_paid = revenue.groupby('customer_id')['service_date'].min().reset_index()
            first_paid.columns = ['customer_id', 'conversion_date']
            
            logger.info(f"Found {len(first_paid)} customers with revenue")
            return first_paid
        
        # For FIRST_BOOKED or FIRST_ATTENDED, would need appointment data
        # These would be implemented similarly to FIRST_PAID
        else:
            raise NotImplementedError(
                f"Conversion type {conversion_type.value} not yet implemented"
            )
    
    def _filter_to_pre_conversion(self,
                                interactions_df: pd.DataFrame,
                                conversion_dates_df: pd.DataFrame) -> pd.DataFrame:
        """Filter interactions to only those before conversion event."""
        
        # If FIRST_CONTACT, no filtering needed
        if self.config.conversion_type == ConversionType.FIRST_CONTACT:
            return interactions_df
        
        # Merge with conversion dates
        df = interactions_df.merge(
            conversion_dates_df,
            on='customer_id',
            how='inner'
        )
        
        # Filter to pre-conversion only
        df = df[df['interaction_date'] <= df['conversion_date']]
        
        # Apply lookback window if configured
        if self.config.lookback_days:
            df['days_before_conversion'] = (
                df['conversion_date'] - df['interaction_date']
            ).dt.days
            df = df[df['days_before_conversion'] <= self.config.lookback_days]
        
        logger.info(f"Filtered to {len(df)} pre-conversion touchpoints")
        return df
    
    def _calculate_credits(self, interactions_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate attribution credit for each touchpoint.
        
        Uses equal-weight per day: all touchpoints on same day share credit equally,
        then normalized so each customer contributes 1.0 total credit.
        """
        df = interactions_df.copy()
        
        # Count touchpoints per customer per day
        daily_counts = df.groupby(
            ['customer_id', 'interaction_date']
        ).size().reset_index(name='touchpoints_this_day')
        
        df = df.merge(daily_counts, on=['customer_id', 'interaction_date'])
        
        # Equal credit per touchpoint on same day
        df['daily_credit'] = 1.0 / df['touchpoints_this_day']
        
        if self.config.normalize_credit:
            # Calculate total credit per customer
            customer_totals = df.groupby('customer_id')['daily_credit'].sum().reset_index()
            customer_totals.columns = ['customer_id', 'customer_total_credit']
            
            df = df.merge(customer_totals, on='customer_id')
            
            # Normalize so each customer sums to 1.0
            df['credit'] = df['daily_credit'] / df['customer_total_credit']
        else:
            df['credit'] = df['daily_credit']
        
        # Filter by minimum threshold
        if self.config.min_credit_threshold > 0:
            df = df[df['credit'] >= self.config.min_credit_threshold]
        
        return df
    
    def _attribute_revenue(self,
                         interactions_df: pd.DataFrame,
                         revenue_df: pd.DataFrame,
                         conversion_dates_df: pd.DataFrame) -> pd.DataFrame:
        """Attribute revenue to touchpoints based on credit."""
        
        df = interactions_df.copy()
        
        # Get first paid revenue per customer
        revenue = revenue_df.copy()
        revenue['service_date'] = revenue['service_date'].apply(parse_date)
        
        # Merge with conversion dates to get first paid revenue
        revenue = revenue.merge(conversion_dates_df, on='customer_id')
        first_revenue = revenue[revenue['service_date'] == revenue['conversion_date']]
        
        first_revenue_agg = first_revenue.groupby('customer_id').agg({
            'net': 'sum'
        }).reset_index()
        first_revenue_agg.columns = ['customer_id', 'first_paid_revenue']
        
        # Also get total lifetime revenue
        total_revenue = revenue.groupby('customer_id')['net'].sum().reset_index()
        total_revenue.columns = ['customer_id', 'total_revenue']
        
        # Merge revenue data
        df = df.merge(first_revenue_agg, on='customer_id', how='left')
        df = df.merge(total_revenue, on='customer_id', how='left')
        
        # Fill NaN with 0
        df['first_paid_revenue'] = df['first_paid_revenue'].fillna(0)
        df['total_revenue'] = df['total_revenue'].fillna(0)
        
        # Calculate attributed revenue
        df['revenue_attributed'] = df['credit'] * df['first_paid_revenue']
        df['total_revenue_attributed'] = df['credit'] * df['total_revenue']
        
        return df
    
    def create_channel_report(self, attribution_df: AttributionDataFrame) -> pd.DataFrame:
        """
        Create summary report by channel.
        
        Args:
            attribution_df: Attribution results
            
        Returns:
            DataFrame with channel-level metrics
        """
        return attribution_df.group_by_channel()


def load_channel_mapping(mapping_file: str) -> Dict[str, str]:
    """
    Load channel mapping from CSV file.
    
    Expected format:
        source,channel
        google_ads,Paid Search
        facebook_ads,Facebook
        ...
    
    Args:
        mapping_file: Path to mapping CSV
        
    Returns:
        Dictionary mapping sources to channels
    """
    try:
        mapping_df = pd.read_csv(mapping_file)
        return dict(zip(mapping_df['source'], mapping_df['channel']))
    except Exception as e:
        logger.error(f"Error loading channel mapping: {e}")
        return {}
