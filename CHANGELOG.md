# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-27

### Added
- Initial release of marketing attribution framework
- Core attribution engine with multi-touch attribution model
- Customer matching via phone, email, and direct ID
- Support for multiple conversion types (first contact, booked, attended, paid)
- Phone number validation against NANPA registry
- Flexible date parsing and handling
- Revenue attribution capabilities
- Channel-level and customer-level reporting
- Comprehensive test suite
- Example scripts and documentation
- Channel mapping configuration
- Attribution result aggregation methods

### Features
- **Attribution Models**
  - Multi-touch time-decay model
  - Equal-weight per day distribution
  - Normalized credit allocation
  - Pre-conversion filtering
  
- **Customer Matching**
  - Phone number matching (up to 4 numbers per customer)
  - Email matching (up to 2 emails per customer)
  - Direct ID matching
  - Automatic normalization and validation
  
- **Data Processing**
  - Pandas-based efficient operations
  - Support for large datasets (100K+ interactions)
  - Flexible date format parsing
  - Configurable lookback windows
  
- **Reporting**
  - Channel-level attribution summary
  - Customer-level attribution breakdown
  - First-touch and last-touch analysis
  - Revenue attribution by channel
  - CSV export functionality

### Documentation
- Comprehensive README with quick start guide
- System architecture documentation
- Code examples and tutorials
- API documentation via docstrings
- Testing documentation

### Technical
- Python 3.8+ support
- Modern type hints throughout
- Structured logging
- Configuration via dataclasses
- Modular, extensible architecture

## [Unreleased]

### Planned Features
- Position-based attribution models
- U-shaped and W-shaped attribution
- Machine learning-based attribution
- Real-time attribution calculation
- API connectors for major platforms
- Dashboard visualization
- A/B testing framework for attribution models

---

## Version History

- **1.0.0** (2025-01-27): Initial release with core functionality
