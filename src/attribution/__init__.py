"""Marketing attribution calculation system."""

from attribution.core import AttributionEngine, load_channel_mapping
from attribution.models import (
    ConversionType,
    AttributionConfig,
    AttributionDataFrame,
    MarketingInteraction,
    Customer,
    RevenueEvent,
    ChannelAttribution
)
from attribution.matchers import CustomerMatcher

__version__ = '1.0.0'

__all__ = [
    'AttributionEngine',
    'load_channel_mapping',
    'ConversionType',
    'AttributionConfig',
    'AttributionDataFrame',
    'CustomerMatcher',
    'MarketingInteraction',
    'Customer',
    'RevenueEvent',
    'ChannelAttribution',
]
