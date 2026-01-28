"""
Example: Basic Attribution Analysis

Demonstrates how to use the marketing attribution system to analyze
marketing touchpoints and calculate revenue attribution by channel.
"""

import pandas as pd
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from attribution import (
    AttributionEngine, 
    AttributionConfig, 
    ConversionType,
    load_channel_mapping
)
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_sample_data():
    """
    Load or create sample data for demonstration.
    
    Returns:
        Tuple of (interactions_df, customers_df, revenue_df)
    """
    
    # Sample marketing interactions (calls, form fills, etc.)
    interactions_data = {
        'id': ['call_001', 'call_002', 'call_003', 'web_001', 'call_004'],
        'contact_number': ['16195551234', '18585552345', '16195551234', '17605553456', '18585552345'],
        'email': [None, 'john@email.com', None, 'jane@email.com', 'john@email.com'],
        'called_at': [
            '2024-01-15T10:30:00',
            '2024-01-18T14:20:00',
            '2024-01-22T09:15:00',
            '2024-01-20T16:45:00',
            '2024-02-05T11:30:00'
        ],
        'source': ['google_ads', 'facebook', 'google_ads', 'organic_search', 'referral'],
        'referral': [None, 'Facebook Ad Campaign', None, 'Google Organic', 'Friend Referral']
    }
    interactions_df = pd.DataFrame(interactions_data)
    
    # Sample customer data
    customers_data = {
        'customer_id': ['PAT001', 'PAT002', 'PAT003'],
        'phone_1': ['(619) 555-1234', '(858) 555-2345', '(760) 555-3456'],
        'phone_2': [None, None, '(619) 555-9999'],
        'email_1': ['alice@email.com', 'john@email.com', 'jane@email.com'],
        'email_2': [None, 'j.doe@work.com', None],
        'referral_source_id': [10, 20, 15]
    }
    customers_df = pd.DataFrame(customers_data)
    
    # Sample revenue data
    revenue_data = {
        'customer_id': ['PAT001', 'PAT001', 'PAT002', 'PAT002', 'PAT003'],
        'service_date': ['2024-01-25', '2024-02-15', '2024-02-01', '2024-03-01', '2024-01-28'],
        'net': [1500.00, 800.00, 2500.00, 1200.00, 950.00],
        'revenue_center': ['Med Spa', 'Med Spa', 'Surgery', 'Surgery', 'Med Spa'],
        'service_category': ['Injectables', 'Laser', 'Cosmetic Surgery', 'Cosmetic Surgery', 'Injectables']
    }
    revenue_df = pd.DataFrame(revenue_data)
    
    return interactions_df, customers_df, revenue_df


def create_channel_mapping():
    """Create mapping from sources to channels."""
    mapping = {
        'google_ads': 'Paid Search',
        'facebook': 'Facebook',
        'facebook_ads': 'Facebook',
        'instagram': 'Instagram',
        'organic_search': 'Organic Search',
        'referral': 'Referral',
        'email': 'Email Marketing',
        'direct': 'Direct'
    }
    return mapping


def main():
    """Run attribution analysis example."""
    
    logger.info("="*60)
    logger.info("Marketing Attribution Analysis Example")
    logger.info("="*60)
    
    # Load data
    logger.info("\n1. Loading sample data...")
    interactions_df, customers_df, revenue_df = load_sample_data()
    
    logger.info(f"   - Interactions: {len(interactions_df)}")
    logger.info(f"   - Customers: {len(customers_df)}")
    logger.info(f"   - Revenue events: {len(revenue_df)}")
    
    # Create channel mapping
    logger.info("\n2. Creating channel mapping...")
    channel_mapping = create_channel_mapping()
    logger.info(f"   - Mapped {len(channel_mapping)} sources to channels")
    
    # Configure attribution
    logger.info("\n3. Configuring attribution engine...")
    config = AttributionConfig(
        conversion_type=ConversionType.FIRST_PAID,
        normalize_credit=True,
        lookback_days=None  # Unlimited lookback
    )
    logger.info(f"   - Conversion type: {config.conversion_type.value}")
    logger.info(f"   - Normalize credit: {config.normalize_credit}")
    
    # Initialize engine
    logger.info("\n4. Initializing attribution engine...")
    engine = AttributionEngine(config)
    
    # Calculate attribution
    logger.info("\n5. Calculating attribution...")
    results = engine.calculate_attribution(
        interactions_df=interactions_df,
        customers_df=customers_df,
        revenue_df=revenue_df,
        channel_mapping=channel_mapping
    )
    
    # Display results
    logger.info("\n6. Attribution Results")
    logger.info("-" * 60)
    logger.info(f"   Total touchpoints: {len(results.df)}")
    logger.info(f"   Unique customers: {results.unique_customers}")
    logger.info(f"   Unique channels: {results.unique_channels}")
    logger.info(f"   Total attribution credit: {results.total_credit:.2f}")
    
    # Channel-level summary
    logger.info("\n7. Channel Attribution Summary")
    logger.info("-" * 60)
    channel_summary = results.group_by_channel()
    
    print("\nChannel Performance:")
    print(channel_summary.to_string(index=False))
    
    # Customer-level attribution
    logger.info("\n8. Customer-Level Attribution")
    logger.info("-" * 60)
    customer_summary = results.group_by_customer()
    print("\nAttribution by Customer:")
    print(customer_summary.to_string(index=False))
    
    # First-touch attribution (for comparison)
    logger.info("\n9. First-Touch Attribution (for comparison)")
    logger.info("-" * 60)
    first_touch = results.get_first_touch_attribution()
    print("\nFirst-Touch Attribution:")
    print(first_touch.to_string(index=False))
    
    # Save results
    logger.info("\n10. Saving results...")
    output_dir = Path(__file__).parent.parent / 'results'
    output_dir.mkdir(exist_ok=True)
    
    results.to_csv(output_dir / 'attribution_detailed.csv')
    channel_summary.to_csv(output_dir / 'attribution_by_channel.csv', index=False)
    customer_summary.to_csv(output_dir / 'attribution_by_customer.csv', index=False)
    
    logger.info(f"   Results saved to {output_dir}")
    
    logger.info("\n" + "="*60)
    logger.info("Analysis Complete!")
    logger.info("="*60)


if __name__ == '__main__':
    main()
