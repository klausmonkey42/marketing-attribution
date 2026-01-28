"""
Customer matching algorithms.

Matches marketing interactions to customers using phone numbers, emails,
and other identifiers.
"""

import pandas as pd
from typing import List, Dict, Optional, Set, Tuple
from utils.phone import normalize_phone, is_valid_phone
import logging

logger = logging.getLogger(__name__)


class CustomerMatcher:
    """
    Matches marketing interactions to customers using multiple identifiers.
    
    Supports matching via:
    - Phone numbers (up to 4 per customer)
    - Email addresses (up to 2 per customer)
    - Direct customer IDs
    """
    
    def __init__(self, customers_df: pd.DataFrame):
        """
        Initialize matcher with customer data.
        
        Args:
            customers_df: DataFrame with columns:
                - customer_id: Unique customer identifier
                - phone_1, phone_2, phone_3, phone_4: Phone numbers (optional)
                - email_1, email_2: Email addresses (optional)
        """
        self.customers_df = customers_df.copy()
        self._prepare_customer_data()
    
    def _prepare_customer_data(self):
        """Normalize phone numbers and prepare lookup structures."""
        # Normalize all phone columns
        phone_cols = [col for col in self.customers_df.columns if col.startswith('phone_')]
        
        for col in phone_cols:
            norm_col = f'{col}_normalized'
            self.customers_df[norm_col] = self.customers_df[col].apply(
                lambda x: normalize_phone(x) if pd.notna(x) else None
            )
        
        # Normalize email addresses (lowercase, strip whitespace)
        email_cols = [col for col in self.customers_df.columns if col.startswith('email_')]
        
        for col in email_cols:
            if col in self.customers_df.columns:
                self.customers_df[col] = self.customers_df[col].apply(
                    lambda x: str(x).lower().strip() if pd.notna(x) and x != '' else None
                )
    
    def match_by_phone(self, interactions_df: pd.DataFrame, 
                       phone_column: str = 'contact_number') -> pd.DataFrame:
        """
        Match interactions to customers by phone number.
        
        Args:
            interactions_df: DataFrame with interaction data
            phone_column: Name of column containing phone numbers
            
        Returns:
            DataFrame with matched interactions including customer_id
        """
        if phone_column not in interactions_df.columns:
            logger.warning(f"Phone column '{phone_column}' not found in interactions")
            return pd.DataFrame()
        
        # Normalize interaction phone numbers
        interactions = interactions_df.copy()
        interactions['phone_normalized'] = interactions[phone_column].apply(
            lambda x: normalize_phone(x) if pd.notna(x) else None
        )
        
        # Filter to valid phones only
        interactions = interactions[interactions['phone_normalized'].notna()]
        
        if len(interactions) == 0:
            logger.warning("No valid phone numbers found in interactions")
            return pd.DataFrame()
        
        # Match against each customer phone field
        matches = []
        phone_cols = [col for col in self.customers_df.columns 
                     if col.startswith('phone_') and col.endswith('_normalized')]
        
        for i, phone_col in enumerate(phone_cols, 1):
            # Create temp dataframe for this phone field
            customer_phones = self.customers_df[
                ['customer_id', phone_col]
            ].copy()
            customer_phones = customer_phones[customer_phones[phone_col].notna()]
            customer_phones = customer_phones.rename(columns={phone_col: 'phone_normalized'})
            
            # Merge with interactions
            matched = interactions.merge(
                customer_phones,
                on='phone_normalized',
                how='inner'
            )
            
            if len(matched) > 0:
                matched['match_type'] = f'phone_{i}'
                matches.append(matched)
                logger.debug(f"Matched {len(matched)} interactions via phone_{i}")
        
        if not matches:
            logger.info("No phone matches found")
            return pd.DataFrame()
        
        # Combine all phone matches
        all_matches = pd.concat(matches, ignore_index=True)
        
        # Remove duplicates (same interaction matched multiple ways)
        all_matches = all_matches.drop_duplicates(
            subset=['id', 'customer_id'] if 'id' in all_matches.columns else ['customer_id']
        )
        
        logger.info(f"Total phone matches: {len(all_matches)}")
        return all_matches
    
    def match_by_email(self, interactions_df: pd.DataFrame, 
                       email_column: str = 'email') -> pd.DataFrame:
        """
        Match interactions to customers by email address.
        
        Args:
            interactions_df: DataFrame with interaction data
            email_column: Name of column containing email addresses
            
        Returns:
            DataFrame with matched interactions including customer_id
        """
        if email_column not in interactions_df.columns:
            logger.warning(f"Email column '{email_column}' not found in interactions")
            return pd.DataFrame()
        
        # Normalize interaction emails
        interactions = interactions_df.copy()
        interactions['email_normalized'] = interactions[email_column].apply(
            lambda x: str(x).lower().strip() if pd.notna(x) and x != '' else None
        )
        
        # Filter to valid emails only
        interactions = interactions[
            (interactions['email_normalized'].notna()) &
            (interactions['email_normalized'] != '') &
            (interactions['email_normalized'].str.contains('@', na=False))
        ]
        
        if len(interactions) == 0:
            logger.warning("No valid email addresses found in interactions")
            return pd.DataFrame()
        
        # Match against each customer email field
        matches = []
        email_cols = [col for col in self.customers_df.columns 
                     if col.startswith('email_') and not col.endswith('_normalized')]
        
        for i, email_col in enumerate(email_cols, 1):
            # Create temp dataframe for this email field
            customer_emails = self.customers_df[
                ['customer_id', email_col]
            ].copy()
            customer_emails = customer_emails[
                (customer_emails[email_col].notna()) &
                (customer_emails[email_col] != '')
            ]
            customer_emails = customer_emails.rename(
                columns={email_col: 'email_normalized'}
            )
            
            # Merge with interactions
            matched = interactions.merge(
                customer_emails,
                on='email_normalized',
                how='inner'
            )
            
            if len(matched) > 0:
                matched['match_type'] = f'email_{i}'
                matches.append(matched)
                logger.debug(f"Matched {len(matched)} interactions via email_{i}")
        
        if not matches:
            logger.info("No email matches found")
            return pd.DataFrame()
        
        # Combine all email matches
        all_matches = pd.concat(matches, ignore_index=True)
        
        # Remove duplicates
        all_matches = all_matches.drop_duplicates(
            subset=['id', 'customer_id'] if 'id' in all_matches.columns else ['customer_id']
        )
        
        logger.info(f"Total email matches: {len(all_matches)}")
        return all_matches
    
    def match_by_id(self, interactions_df: pd.DataFrame, 
                    id_column: str = 'customer_id') -> pd.DataFrame:
        """
        Match interactions that already have a customer ID.
        
        Args:
            interactions_df: DataFrame with interaction data
            id_column: Name of column containing customer IDs
            
        Returns:
            DataFrame with matched interactions
        """
        if id_column not in interactions_df.columns:
            return pd.DataFrame()
        
        # Filter to rows with valid customer IDs
        matched = interactions_df[
            interactions_df[id_column].notna() &
            (interactions_df[id_column] != '')
        ].copy()
        
        # Verify customer IDs exist in customer database
        valid_customer_ids = set(self.customers_df['customer_id'].unique())
        matched = matched[matched[id_column].isin(valid_customer_ids)]
        
        if len(matched) > 0:
            matched['match_type'] = 'direct_id'
            logger.info(f"Direct ID matches: {len(matched)}")
        
        return matched
    
    def match_all(self, interactions_df: pd.DataFrame) -> pd.DataFrame:
        """
        Match interactions using all available methods.
        
        Combines matches from phone, email, and direct ID matching,
        removing duplicates and preferring direct ID matches.
        
        Args:
            interactions_df: DataFrame with interaction data
            
        Returns:
            DataFrame with all matched interactions
        """
        logger.info(f"Matching {len(interactions_df)} interactions to customers...")
        
        matches = []
        
        # Try phone matching
        phone_matches = self.match_by_phone(interactions_df)
        if len(phone_matches) > 0:
            matches.append(phone_matches)
        
        # Try email matching
        email_matches = self.match_by_email(interactions_df)
        if len(email_matches) > 0:
            matches.append(email_matches)
        
        # Try direct ID matching
        id_matches = self.match_by_id(interactions_df)
        if len(id_matches) > 0:
            matches.append(id_matches)
        
        if not matches:
            logger.warning("No matches found using any method")
            return pd.DataFrame()
        
        # Combine all matches
        all_matches = pd.concat(matches, ignore_index=True)
        
        # Remove duplicates, keeping first match (direct ID is first in list)
        id_col = 'id' if 'id' in all_matches.columns else None
        if id_col:
            all_matches = all_matches.drop_duplicates(
                subset=[id_col, 'customer_id'],
                keep='first'
            )
            
            # If same interaction matched to multiple customers, keep first
            all_matches = all_matches.drop_duplicates(
                subset=[id_col],
                keep='first'
            )
        
        logger.info(
            f"Successfully matched {len(all_matches)} interactions "
            f"to {all_matches['customer_id'].nunique()} unique customers"
        )
        
        return all_matches
    
    def get_match_statistics(self, matched_df: pd.DataFrame) -> Dict:
        """
        Calculate matching statistics.
        
        Args:
            matched_df: DataFrame returned from match_all()
            
        Returns:
            Dictionary with match statistics
        """
        if len(matched_df) == 0:
            return {
                'total_matches': 0,
                'unique_customers': 0,
                'phone_matches': 0,
                'email_matches': 0,
                'direct_id_matches': 0
            }
        
        stats = {
            'total_matches': len(matched_df),
            'unique_customers': matched_df['customer_id'].nunique(),
        }
        
        if 'match_type' in matched_df.columns:
            stats['phone_matches'] = len(
                matched_df[matched_df['match_type'].str.startswith('phone')]
            )
            stats['email_matches'] = len(
                matched_df[matched_df['match_type'].str.startswith('email')]
            )
            stats['direct_id_matches'] = len(
                matched_df[matched_df['match_type'] == 'direct_id']
            )
        
        return stats
