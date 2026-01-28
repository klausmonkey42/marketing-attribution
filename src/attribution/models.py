"""
Data models and schemas for attribution analysis.

Defines the structure of inputs and outputs for the attribution system.
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import List, Optional, Dict
import pandas as pd


class ConversionType(Enum):
    """Defines the conversion event for attribution."""
    FIRST_CONTACT = "first_contact"      # Any customer interaction
    FIRST_BOOKED = "first_booked"        # First appointment booked
    FIRST_ATTENDED = "first_attended"    # First attended appointment
    FIRST_PAID = "first_paid"            # First revenue-generating event


@dataclass
class MarketingInteraction:
    """Represents a single marketing touchpoint."""
    interaction_id: str
    customer_id: Optional[str]
    interaction_date: date
    channel: str
    source: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    metadata: Dict = field(default_factory=dict)


@dataclass
class Customer:
    """Represents a customer with contact information."""
    customer_id: str
    phones: List[str] = field(default_factory=list)
    emails: List[str] = field(default_factory=list)
    referral_source: Optional[str] = None
    first_contact_date: Optional[date] = None
    first_booked_date: Optional[date] = None
    first_attended_date: Optional[date] = None
    first_paid_date: Optional[date] = None


@dataclass
class RevenueEvent:
    """Represents a revenue-generating event."""
    customer_id: str
    service_date: date
    revenue_amount: float
    revenue_center: Optional[str] = None
    service_category: Optional[str] = None
    

@dataclass
class AttributionCredit:
    """Represents attribution credit for a single touchpoint."""
    customer_id: str
    interaction_id: str
    interaction_date: date
    channel: str
    credit: float
    revenue_attributed: float = 0.0


@dataclass
class ChannelAttribution:
    """Aggregated attribution results by channel."""
    channel: str
    total_credit: float
    customer_count: int
    total_revenue: float
    avg_revenue_per_customer: float
    first_touch_count: int = 0
    last_touch_count: int = 0


class AttributionDataFrame:
    """
    Wrapper for attribution results stored as pandas DataFrames.
    
    Provides convenient methods for accessing and transforming attribution data.
    """
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize with a DataFrame containing attribution results.
        
        Expected columns:
        - customer_id: Customer identifier
        - channel: Marketing channel
        - interaction_date: Date of touchpoint
        - credit: Attribution credit (0-1)
        - revenue_attributed: Revenue attributed to this touchpoint
        """
        self.df = df
        self._validate_schema()
    
    def _validate_schema(self):
        """Validate that required columns are present."""
        required_cols = ['customer_id', 'channel', 'credit']
        missing = [col for col in required_cols if col not in self.df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
    
    def group_by_channel(self) -> pd.DataFrame:
        """
        Aggregate attribution by channel.
        
        Returns:
            DataFrame with columns: channel, total_credit, customer_count,
            total_revenue, avg_revenue_per_customer
        """
        agg_dict = {
            'credit': 'sum',
            'customer_id': 'nunique',
        }
        
        if 'revenue_attributed' in self.df.columns:
            agg_dict['revenue_attributed'] = 'sum'
        
        result = self.df.groupby('channel').agg(agg_dict).reset_index()
        result.columns = ['channel', 'total_credit', 'customer_count', 'total_revenue']
        
        # Calculate average revenue per customer
        result['avg_revenue_per_customer'] = (
            result['total_revenue'] / result['customer_count']
        ).fillna(0)
        
        return result.sort_values('total_revenue', ascending=False)
    
    def group_by_customer(self) -> pd.DataFrame:
        """
        Aggregate attribution by customer.
        
        Returns:
            DataFrame with customer-level attribution across all channels
        """
        # Pivot to get channel credits as columns
        pivot = self.df.pivot_table(
            index='customer_id',
            columns='channel',
            values='credit',
            aggfunc='sum',
            fill_value=0
        ).reset_index()
        
        # Add total revenue if available
        if 'revenue_attributed' in self.df.columns:
            revenue = self.df.groupby('customer_id')['revenue_attributed'].sum()
            pivot = pivot.merge(
                revenue.rename('total_revenue'),
                on='customer_id',
                how='left'
            )
        
        return pivot
    
    def filter_by_date_range(self, start_date: date, end_date: date) -> 'AttributionDataFrame':
        """
        Filter attribution to a specific date range.
        
        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            
        Returns:
            New AttributionDataFrame with filtered data
        """
        if 'interaction_date' not in self.df.columns:
            raise ValueError("DataFrame must have 'interaction_date' column")
        
        mask = (
            (self.df['interaction_date'] >= start_date) &
            (self.df['interaction_date'] <= end_date)
        )
        return AttributionDataFrame(self.df[mask].copy())
    
    def get_first_touch_attribution(self) -> pd.DataFrame:
        """
        Get first-touch attribution (credit to earliest interaction per customer).
        
        Returns:
            DataFrame with first-touch attribution
        """
        if 'interaction_date' not in self.df.columns:
            raise ValueError("DataFrame must have 'interaction_date' column")
        
        # Get first interaction per customer
        first_touch = self.df.sort_values('interaction_date').groupby('customer_id').first()
        
        # Aggregate by channel
        return first_touch.groupby('channel').agg({
            'credit': 'sum',
            'customer_id': 'count'
        }).reset_index()
    
    def get_last_touch_attribution(self) -> pd.DataFrame:
        """
        Get last-touch attribution (credit to latest interaction per customer).
        
        Returns:
            DataFrame with last-touch attribution
        """
        if 'interaction_date' not in self.df.columns:
            raise ValueError("DataFrame must have 'interaction_date' column")
        
        # Get last interaction per customer
        last_touch = self.df.sort_values('interaction_date').groupby('customer_id').last()
        
        # Aggregate by channel
        return last_touch.groupby('channel').agg({
            'credit': 'sum',
            'customer_id': 'count'
        }).reset_index()
    
    def to_csv(self, path: str, **kwargs):
        """Save attribution data to CSV."""
        self.df.to_csv(path, index=False, **kwargs)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return self.df.to_dict(orient='records')
    
    @property
    def total_credit(self) -> float:
        """Total attribution credit across all touchpoints."""
        return self.df['credit'].sum()
    
    @property
    def unique_customers(self) -> int:
        """Number of unique customers in attribution."""
        return self.df['customer_id'].nunique()
    
    @property
    def unique_channels(self) -> int:
        """Number of unique channels in attribution."""
        return self.df['channel'].nunique()


@dataclass
class AttributionConfig:
    """Configuration for attribution calculation."""
    conversion_type: ConversionType = ConversionType.FIRST_PAID
    lookback_days: Optional[int] = None  # None = unlimited lookback
    normalize_credit: bool = True  # Normalize credit to sum to 1.0 per customer
    min_credit_threshold: float = 0.0  # Minimum credit to include in results
