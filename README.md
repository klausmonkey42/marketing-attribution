# Marketing Attribution Analytics

A production-ready Python framework for multi-touch marketing attribution analysis, designed to track customer journeys across multiple touchpoints and calculate revenue attribution by channel.

## Overview

This system implements a flexible multi-touch attribution model that:
- Integrates data from call tracking systems (CTM) and CRM/EHR platforms
- Matches customer interactions across phone, email, and web touchpoints
- Calculates time-decay weighted attribution across marketing channels
- Links revenue back to original marketing sources
- Supports multiple conversion definitions (first contact, booked, attended, paid)

## Features

- **Multi-Source Integration**: Combines call tracking, CRM, and transaction data
- **Flexible Attribution Models**: Supports multiple conversion types and weighting strategies
- **Phone Number Normalization**: Validates and standardizes US/Canadian phone numbers
- **Email Matching**: Cross-references customer email addresses across systems
- **Revenue Attribution**: Connects marketing touchpoints to actual revenue
- **Channel Mapping**: Flexible configuration for categorizing marketing sources

## Project Structure

```
marketing-attribution/
├── src/
│   ├── attribution/
│   │   ├── __init__.py
│   │   ├── core.py           # Core attribution logic
│   │   ├── matchers.py       # Customer matching algorithms
│   │   └── models.py         # Data models and schemas
│   ├── data/
│   │   ├── __init__.py
│   │   ├── extractors.py     # Data extraction from sources
│   │   ├── loaders.py        # Data loading utilities
│   │   └── transformers.py   # Data transformation functions
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── phone.py          # Phone number utilities
│   │   ├── date.py           # Date handling utilities
│   │   └── validation.py     # Data validation
│   └── config/
│       ├── __init__.py
│       └── settings.py       # Configuration management
├── tests/
│   ├── test_attribution.py
│   ├── test_matchers.py
│   └── test_utils.py
├── examples/
│   ├── basic_attribution.py
│   └── revenue_analysis.py
├── data/
│   ├── mappings/
│   │   ├── channel_mapping.csv
│   │   └── source_mapping.csv
│   └── sample/              # Sample data for testing
├── requirements.txt
└── setup.py
```

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/marketing-attribution.git
cd marketing-attribution

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

## Quick Start

```python
from attribution import AttributionEngine, ConversionType
from data import DataLoader

# Initialize the attribution engine
engine = AttributionEngine(
    conversion_type=ConversionType.FIRST_PAID
)

# Load your data
loader = DataLoader(config_path='config.yaml')
call_data = loader.load_call_tracking_data()
patient_data = loader.load_patient_data()
revenue_data = loader.load_revenue_data()

# Run attribution analysis
results = engine.calculate_attribution(
    interactions=call_data,
    customers=patient_data,
    revenue=revenue_data
)

# Get attribution by channel
channel_attribution = results.group_by_channel()
print(channel_attribution)
```

## Attribution Models

### Conversion Types

- **First Contact**: Attribution to first interaction with any customer
- **First Booked**: Attribution to interactions before first appointment booking
- **First Attended**: Attribution to interactions before first attended appointment
- **First Paid**: Attribution to interactions before first revenue-generating event

### Attribution Weights

The system uses a **time-decay** model where:
- Multiple touchpoints on the same day share credit equally
- Only touchpoints before the conversion event receive credit
- Credit is normalized so each customer contributes 1.0 total attribution

## Configuration

Create a `config.yaml` file:

```yaml
# Data sources
data:
  call_tracking:
    format: csv
    path: data/raw/call_tracking.csv
  
  customers:
    format: csv
    path: data/raw/customers.csv
  
  revenue:
    format: csv
    path: data/raw/revenue.csv

# Attribution settings
attribution:
  conversion_type: first_paid
  lookback_days: 365
  
# Channel mappings
mappings:
  channel_map: data/mappings/channel_mapping.csv
  source_map: data/mappings/source_mapping.csv

# Output settings
output:
  path: results/
  format: csv
```

## Data Requirements

### Call Tracking Data
Required fields:
- `id`: Unique interaction ID
- `contact_number`: Phone number
- `email`: Email address
- `called_at`: Timestamp
- `source`: Marketing source
- `referral`: Referral information

### Customer Data
Required fields:
- `patient_id`: Unique customer ID
- `phone_1`, `phone_2`, etc.: Contact phone numbers
- `email_1`, `email_2`: Email addresses
- `referral_source_id`: CRM referral source

### Revenue Data
Required fields:
- `patient_id`: Customer ID
- `service_date`: Date of service
- `net`: Revenue amount
- `revenue_center`: Revenue category

## Advanced Usage

### Custom Attribution Models

```python
from attribution import CustomAttributionModel

# Define custom weighting function
def exponential_decay(days_before_conversion):
    return 0.5 ** (days_before_conversion / 7)

model = CustomAttributionModel(
    weight_function=exponential_decay,
    normalize=True
)

engine = AttributionEngine(model=model)
```

### Channel Grouping

```python
# Define channel hierarchies
channel_groups = {
    'Paid Digital': ['Paid Search', 'Facebook', 'Instagram', 'Youtube'],
    'Organic': ['Organic Search', 'Referral', 'Email'],
    'Direct': ['Event Promotion', 'Business Development']
}

results = engine.calculate_attribution(
    interactions=call_data,
    customers=patient_data,
    revenue=revenue_data,
    channel_groups=channel_groups
)
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_attribution.py -v
```

## Performance Considerations

- **Large Datasets**: The matcher module uses pandas merge operations optimized for large datasets
- **Memory**: For datasets >1M rows, consider chunked processing
- **Caching**: Phone number validation results are cached to improve performance

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Citation

If you use this code in your research or application, please cite:

```bibtex
@software{marketing_attribution,
  title = {Marketing Attribution Analytics Framework},
  author = {Your Name},
  year = {2025},
  url = {https://github.com/yourusername/marketing-attribution}
}
```

## Contact

For questions or support, please open an issue on GitHub or contact [your.email@example.com]

---

**Built for analytics professionals who need production-ready attribution modeling.**
