# System Architecture

## Overview

The marketing attribution system is designed with a modular, production-ready architecture that separates concerns and enables easy testing and extension.

## Architecture Principles

1. **Separation of Concerns**: Data loading, matching, attribution calculation, and reporting are separate modules
2. **Composability**: Components can be used independently or together
3. **Testability**: All modules have clear interfaces and can be unit tested
4. **Extensibility**: New attribution models, matchers, and data sources can be added easily
5. **Performance**: Uses pandas for efficient operations on large datasets

## Component Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Attribution System                       │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
   ┌────▼────┐          ┌────▼────┐          ┌────▼────┐
   │  Utils  │          │  Data   │          │Attribution│
   └────┬────┘          └────┬────┘          └────┬────┘
        │                     │                     │
   ┌────▼────┐          ┌────▼────┐          ┌────▼────┐
   │ phone.py│          │matchers │          │ core.py │
   │ date.py │          │         │          │models.py│
   └─────────┘          └─────────┘          └─────────┘
```

## Core Components

### 1. Utilities (`src/utils/`)

#### `phone.py`
- **Purpose**: Phone number validation and normalization
- **Key Functions**:
  - `is_valid_phone()`: Validates against NANPA registry
  - `normalize_phone()`: Standardizes format
  - `phones_match()`: Compares phone numbers
- **Performance**: Uses `@lru_cache` for validation results

#### `date.py`
- **Purpose**: Date parsing and comparison
- **Key Functions**:
  - `parse_date()`: Flexible date parsing
  - `is_before()`, `is_after()`: Date comparisons
  - `days_between()`: Date arithmetic
- **Handles**: Multiple date formats, timezones, edge cases

### 2. Attribution (`src/attribution/`)

#### `models.py`
- **Purpose**: Data structures and schemas
- **Key Classes**:
  - `ConversionType`: Enum for conversion definitions
  - `AttributionConfig`: Configuration object
  - `AttributionDataFrame`: Wrapper with convenience methods
- **Design**: Uses dataclasses for clean, typed structures

#### `matchers.py`
- **Purpose**: Match interactions to customers
- **Key Class**: `CustomerMatcher`
- **Matching Methods**:
  - `match_by_phone()`: Matches via up to 4 phone numbers
  - `match_by_email()`: Matches via up to 2 emails
  - `match_by_id()`: Direct ID matching
  - `match_all()`: Combines all methods
- **Performance**: Uses pandas merge operations optimized for large datasets

#### `core.py`
- **Purpose**: Attribution calculation engine
- **Key Class**: `AttributionEngine`
- **Process**:
  1. Match interactions to customers
  2. Determine conversion events
  3. Filter to pre-conversion touchpoints
  4. Calculate attribution credits
  5. Attribute revenue
- **Flexibility**: Configurable conversion types and credit allocation

## Data Flow

```
┌──────────────┐
│ Raw Data     │
│ - Calls      │
│ - Emails     │
│ - Web Forms  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Data Prep    │
│ - Parse dates│
│ - Normalize  │
│ - Validate   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Customer     │
│ Matching     │
│ - Phone      │
│ - Email      │
│ - Direct ID  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Attribution  │
│ Calculation  │
│ - Filter     │
│ - Weight     │
│ - Normalize  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Revenue      │
│ Attribution  │
│ - Join       │
│ - Distribute │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Results      │
│ - By Channel │
│ - By Customer│
│ - Reports    │
└──────────────┘
```

## Attribution Algorithm

### Multi-Touch Attribution Model

The system implements a **time-decay weighted** multi-touch attribution model:

1. **Touchpoint Collection**: Gather all marketing interactions for each customer
2. **Pre-Conversion Filter**: Only touchpoints before conversion event are credited
3. **Daily Aggregation**: Multiple touchpoints on same day share credit equally
4. **Normalization**: Credits normalized so each customer contributes 1.0 total
5. **Revenue Distribution**: Revenue distributed proportional to attribution credit

### Formula

For customer *c* with touchpoints *T = {t₁, t₂, ..., tₙ}*:

1. **Daily Credit**: If *m* touchpoints occur on day *d*:
   ```
   credit_daily(t) = 1/m
   ```

2. **Customer Total**:
   ```
   total_credit(c) = Σ credit_daily(t) for all t in T
   ```

3. **Normalized Credit**:
   ```
   credit_normalized(t) = credit_daily(t) / total_credit(c)
   ```

4. **Revenue Attribution**:
   ```
   revenue_attributed(t) = credit_normalized(t) × revenue(c)
   ```

### Conversion Types

The system supports multiple conversion definitions:

- **FIRST_CONTACT**: Credit all interactions (no filtering)
- **FIRST_BOOKED**: Credit touchpoints before first appointment booking
- **FIRST_ATTENDED**: Credit touchpoints before first attended appointment
- **FIRST_PAID**: Credit touchpoints before first revenue event (default)

## Performance Considerations

### Scalability

- **Target Scale**: Designed for 100K-1M interactions, 10K-100K customers
- **Memory**: Uses pandas DataFrames with efficient operations
- **CPU**: Vectorized operations where possible
- **I/O**: Reads/writes standard CSV format

### Optimization Techniques

1. **Phone Validation Caching**: Results cached with `@lru_cache`
2. **Vectorized Operations**: Uses pandas/numpy for bulk operations
3. **Early Filtering**: Filters invalid data before expensive operations
4. **Efficient Joins**: Uses pandas merge with appropriate join types

### Performance Tips

- For very large datasets (>1M rows), consider chunked processing
- Pre-filter data to relevant time periods before attribution
- Use appropriate hardware (16GB+ RAM for 1M+ interactions)

## Extension Points

### Adding New Attribution Models

Create custom weight function:

```python
def exponential_decay(days_before_conversion):
    return 0.5 ** (days_before_conversion / 7)

model = CustomAttributionModel(
    weight_function=exponential_decay
)
```

### Adding New Data Sources

Implement new matcher in `matchers.py`:

```python
def match_by_custom_id(self, interactions_df, id_column):
    # Your custom matching logic
    pass
```

### Adding New Conversion Types

1. Add to `ConversionType` enum in `models.py`
2. Implement in `_get_conversion_dates()` in `core.py`

## Error Handling

The system includes comprehensive error handling:

- **Validation Errors**: Invalid phone numbers, dates logged and filtered
- **Missing Data**: Graceful handling of missing columns/values
- **Match Failures**: Reports matching statistics, continues with available matches
- **Configuration Errors**: Clear error messages for invalid configurations

## Logging

Structured logging throughout:

- **INFO**: Key milestones and statistics
- **WARNING**: Data quality issues, missing data
- **DEBUG**: Detailed matching and calculation steps
- **ERROR**: System failures, invalid configurations

## Testing Strategy

1. **Unit Tests**: Individual functions and utilities
2. **Integration Tests**: End-to-end attribution calculations
3. **Data Quality Tests**: Validation of input/output data
4. **Performance Tests**: Benchmarks for large datasets

## Security Considerations

- **PII Handling**: Phone numbers and emails are sensitive data
- **Data Access**: No hardcoded credentials
- **Data Storage**: Results contain customer IDs - secure appropriately
- **Logging**: Avoid logging full PII in production

## Future Enhancements

Potential areas for expansion:

1. **Additional Models**: Position-based, U-shaped attribution
2. **Machine Learning**: Predictive attribution based on historical conversions
3. **Real-time Processing**: Streaming attribution calculations
4. **Data Lake Integration**: Direct connectors to cloud data platforms
5. **Web UI**: Dashboard for visualizing attribution results
6. **A/B Testing**: Framework for testing attribution models

---

**Last Updated**: January 2025
**Version**: 1.0.0
