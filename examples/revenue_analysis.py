"""
Example: Revenue Attribution Analysis

Demonstrates how to calculate ROI and revenue attribution by marketing channel,
including cost data and performance metrics.
"""

import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from attribution import (
    AttributionEngine,
    AttributionConfig,
    ConversionType,
    load_channel_mapping
)
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_sample_data_with_costs():
    """Load sample data including marketing costs."""
    
    # Marketing interactions
    interactions_data = {
        'id': [f'int_{i:03d}' for i in range(1, 21)],
        'contact_number': [
            '16195551234', '18585552345', '16195551234', '17605553456', '18585552345',
            '16195551234', '18585552345', '17605553456', '19495554567', '16195551234',
            '18585552345', '17605553456', '16195551234', '19495554567', '18585552345',
            '17605553456', '16195551234', '19495554567', '18585552345', '17605553456'
        ],
        'called_at': [
            '2024-01-15T10:30:00', '2024-01-16T14:20:00', '2024-01-17T09:15:00',
            '2024-01-18T16:45:00', '2024-01-19T11:30:00', '2024-01-20T15:00:00',
            '2024-01-22T10:00:00', '2024-01-23T13:30:00', '2024-01-24T09:00:00',
            '2024-01-25T14:00:00', '2024-01-26T11:00:00', '2024-01-27T16:00:00',
            '2024-01-28T10:30:00', '2024-01-29T13:00:00', '2024-01-30T15:30:00',
            '2024-02-01T09:00:00', '2024-02-02T14:00:00', '2024-02-03T11:00:00',
            '2024-02-04T16:00:00', '2024-02-05T10:00:00'
        ],
        'source': [
            'google_ads', 'facebook', 'google_ads', 'organic_search', 'referral',
            'email', 'facebook', 'organic_search', 'google_ads', 'email',
            'facebook', 'organic_search', 'google_ads', 'yelp', 'referral',
            'instagram', 'google_ads', 'youtube', 'facebook', 'organic_search'
        ]
    }
    interactions_df = pd.DataFrame(interactions_data)
    
    # Customer data
    customers_data = {
        'customer_id': ['PAT001', 'PAT002', 'PAT003', 'PAT004'],
        'phone_1': ['(619) 555-1234', '(858) 555-2345', '(760) 555-3456', '(949) 555-4567'],
        'email_1': ['alice@email.com', 'john@email.com', 'jane@email.com', 'bob@email.com']
    }
    customers_df = pd.DataFrame(customers_data)
    
    # Revenue data
    revenue_data = {
        'customer_id': ['PAT001', 'PAT001', 'PAT002', 'PAT002', 'PAT003', 'PAT003', 'PAT004'],
        'service_date': ['2024-01-28', '2024-02-15', '2024-02-01', '2024-03-01', 
                        '2024-02-05', '2024-02-20', '2024-02-10'],
        'net': [1500.00, 800.00, 2500.00, 1200.00, 950.00, 650.00, 3200.00],
        'revenue_center': ['Med Spa', 'Med Spa', 'Surgery', 'Surgery', 
                          'Med Spa', 'Med Spa', 'Surgery']
    }
    revenue_df = pd.DataFrame(revenue_data)
    
    # Marketing costs by channel
    costs_data = {
        'channel': [
            'Paid Search', 'Facebook', 'Instagram', 'Youtube', 
            'Organic Search', 'Email Marketing', 'Referral', 'Yelp'
        ],
        'monthly_cost': [
            5000.00, 3000.00, 2000.00, 1500.00,
            0.00, 500.00, 0.00, 300.00
        ],
        'cost_per_interaction': [
            50.00, 25.00, 20.00, 30.00,
            0.00, 5.00, 0.00, 10.00
        ]
    }
    costs_df = pd.DataFrame(costs_data)
    
    return interactions_df, customers_df, revenue_df, costs_df


def calculate_roi_metrics(attribution_df, costs_df):
    """Calculate ROI and performance metrics by channel."""
    
    # Get channel summary
    channel_summary = attribution_df.group_by_channel()
    
    # Merge with costs
    metrics = channel_summary.merge(costs_df, on='channel', how='left')
    metrics['monthly_cost'] = metrics['monthly_cost'].fillna(0)
    metrics['cost_per_interaction'] = metrics['cost_per_interaction'].fillna(0)
    
    # Calculate metrics
    metrics['roi'] = ((metrics['total_revenue'] - metrics['monthly_cost']) 
                     / metrics['monthly_cost']).replace([float('inf'), -float('inf')], 0)
    
    metrics['cost_per_customer'] = (metrics['monthly_cost'] / 
                                   metrics['customer_count']).replace([float('inf')], 0)
    
    metrics['revenue_per_dollar'] = (metrics['total_revenue'] / 
                                    metrics['monthly_cost']).replace([float('inf')], 0)
    
    metrics['profit'] = metrics['total_revenue'] - metrics['monthly_cost']
    
    # Sort by total revenue
    metrics = metrics.sort_values('total_revenue', ascending=False)
    
    return metrics


def main():
    """Run revenue attribution analysis."""
    
    logger.info("="*70)
    logger.info("Revenue Attribution & ROI Analysis")
    logger.info("="*70)
    
    # Load data
    logger.info("\n1. Loading data...")
    interactions_df, customers_df, revenue_df, costs_df = load_sample_data_with_costs()
    
    logger.info(f"   - Interactions: {len(interactions_df)}")
    logger.info(f"   - Customers: {len(customers_df)}")
    logger.info(f"   - Revenue events: {len(revenue_df)}")
    logger.info(f"   - Total revenue: ${revenue_df['net'].sum():,.2f}")
    
    # Channel mapping
    channel_mapping = {
        'google_ads': 'Paid Search',
        'facebook': 'Facebook',
        'instagram': 'Instagram',
        'youtube': 'Youtube',
        'organic_search': 'Organic Search',
        'email': 'Email Marketing',
        'referral': 'Referral',
        'yelp': 'Yelp'
    }
    
    # Configure and run attribution
    logger.info("\n2. Calculating attribution...")
    config = AttributionConfig(
        conversion_type=ConversionType.FIRST_PAID,
        normalize_credit=True
    )
    
    engine = AttributionEngine(config)
    results = engine.calculate_attribution(
        interactions_df=interactions_df,
        customers_df=customers_df,
        revenue_df=revenue_df,
        channel_mapping=channel_mapping
    )
    
    # Calculate ROI metrics
    logger.info("\n3. Calculating ROI metrics...")
    roi_metrics = calculate_roi_metrics(results, costs_df)
    
    # Display results
    logger.info("\n4. Channel Performance & ROI Analysis")
    logger.info("="*70)
    
    print("\n" + "="*70)
    print("CHANNEL ATTRIBUTION & ROI SUMMARY")
    print("="*70)
    
    display_cols = [
        'channel', 'customer_count', 'total_revenue', 
        'monthly_cost', 'profit', 'roi', 'revenue_per_dollar'
    ]
    
    display_df = roi_metrics[display_cols].copy()
    display_df['total_revenue'] = display_df['total_revenue'].apply(lambda x: f"${x:,.2f}")
    display_df['monthly_cost'] = display_df['monthly_cost'].apply(lambda x: f"${x:,.2f}")
    display_df['profit'] = display_df['profit'].apply(lambda x: f"${x:,.2f}")
    display_df['roi'] = display_df['roi'].apply(lambda x: f"{x:.1%}")
    display_df['revenue_per_dollar'] = display_df['revenue_per_dollar'].apply(lambda x: f"${x:.2f}")
    
    print("\n" + display_df.to_string(index=False))
    
    # Key insights
    print("\n" + "="*70)
    print("KEY INSIGHTS")
    print("="*70)
    
    total_attributed_revenue = roi_metrics['total_revenue'].sum()
    total_cost = roi_metrics['monthly_cost'].sum()
    total_profit = total_attributed_revenue - total_cost
    overall_roi = (total_profit / total_cost) * 100 if total_cost > 0 else 0
    
    print(f"\nOverall Performance:")
    print(f"  • Total Revenue Attributed: ${total_attributed_revenue:,.2f}")
    print(f"  • Total Marketing Cost: ${total_cost:,.2f}")
    print(f"  • Total Profit: ${total_profit:,.2f}")
    print(f"  • Overall ROI: {overall_roi:.1f}%")
    
    # Best performing channels
    top_roi = roi_metrics.nlargest(3, 'roi')
    print(f"\nTop ROI Channels:")
    for idx, row in top_roi.iterrows():
        if row['monthly_cost'] > 0:
            print(f"  • {row['channel']}: {row['roi']:.1%} ROI, ${row['profit']:,.2f} profit")
    
    # Most efficient channels
    top_efficiency = roi_metrics[roi_metrics['monthly_cost'] > 0].nlargest(3, 'revenue_per_dollar')
    print(f"\nMost Efficient Channels (Revenue per $1 spent):")
    for idx, row in top_efficiency.iterrows():
        print(f"  • {row['channel']}: ${row['revenue_per_dollar']:.2f} per dollar")
    
    # Recommendations
    print(f"\nRecommendations:")
    
    # Channels with negative ROI
    negative_roi = roi_metrics[
        (roi_metrics['monthly_cost'] > 0) & (roi_metrics['roi'] < 0)
    ]
    if len(negative_roi) > 0:
        print(f"  ⚠ Consider reducing spend on:")
        for idx, row in negative_roi.iterrows():
            print(f"    - {row['channel']} (ROI: {row['roi']:.1%})")
    
    # High ROI channels
    high_roi = roi_metrics[
        (roi_metrics['monthly_cost'] > 0) & (roi_metrics['roi'] > 2.0)
    ]
    if len(high_roi) > 0:
        print(f"  ✓ Consider increasing spend on:")
        for idx, row in high_roi.iterrows():
            print(f"    - {row['channel']} (ROI: {row['roi']:.1%})")
    
    # Free channels performing well
    free_channels = roi_metrics[
        (roi_metrics['monthly_cost'] == 0) & (roi_metrics['total_revenue'] > 1000)
    ]
    if len(free_channels) > 0:
        print(f"  ✓ High-value organic channels to nurture:")
        for idx, row in free_channels.iterrows():
            print(f"    - {row['channel']} (${row['total_revenue']:,.2f} attributed)")
    
    # Save results
    logger.info("\n5. Saving results...")
    output_dir = Path(__file__).parent.parent / 'results'
    output_dir.mkdir(exist_ok=True)
    
    roi_metrics.to_csv(output_dir / 'roi_analysis.csv', index=False)
    results.to_csv(output_dir / 'attribution_with_revenue.csv')
    
    logger.info(f"   Results saved to {output_dir}")
    
    print("\n" + "="*70)
    logger.info("Analysis Complete!")
    print("="*70 + "\n")


if __name__ == '__main__':
    main()
