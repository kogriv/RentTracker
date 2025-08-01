# Overview

Garage Payment Tracker is a fully functional Python-based command-line application that manages and tracks rental payments for garage units. The system successfully automates the process of matching bank statement transactions to expected garage rental payments, determining payment statuses, and generating comprehensive Excel reports. It features automatic payment period detection from bank statements, eliminating manual date configuration errors. The application follows Clean Architecture principles with clear separation between domain logic, application services, and infrastructure components.

**Status**: ✅ FULLY OPERATIONAL - Successfully processing real garage registry and bank statement data with automatic period detection, enhanced payment matching (46.7% coverage with improved accuracy), comprehensive reporting capabilities with metadata headers, clean user interface with hidden technical logs, and fully corrected Days Overdue calculations for all payment statuses (August 2025).

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Core Architecture Pattern
The application follows Clean Architecture with four distinct layers:

1. **Domain Layer** (`src/core/`): Contains business models (Garage, Payment, Transaction, Report) and core services (PaymentMatcher, DateCalculator, StatusDeterminer). This layer is framework-agnostic and contains the essential business logic.

2. **Application Layer** (`src/application/`): Implements use cases (ProcessPayments, GenerateReport) that orchestrate domain services. Uses DTOs for request/response handling to maintain clean boundaries.

3. **Infrastructure Layer** (`src/infrastructure/`): Handles external concerns like file I/O (Excel reading/writing), configuration management, and localization. Includes parsers for different bank statement formats.

4. **Interface Layer** (`src/interfaces/`): Currently implements CLI interface with Click framework. Designed to support future web and bot interfaces.

## Key Architectural Decisions

### User Interface Improvements (August 2025)
Enhanced CLI interface with comprehensive user guidance:
- **Real-time period detection display**: Shows detected payment period immediately upon file discovery
- **Detailed menu descriptions**: Each command includes purpose, recommended usage, and date ranges
- **Visual result separation**: Processing results clearly separated from logs with ASCII borders
- **Interactive guidance**: Custom analysis date option includes recommended ranges and principles
- **Clean console output**: All technical logs redirected to files, console shows only user-relevant results
- **Report metadata**: Added generation date and analysis date in Excel report headers

### Report Enhancements (August 2025)
Comprehensive improvements to Excel report generation:
- **Metadata headers**: Report generation date and analysis date displayed in top rows
- **Enhanced status determination**: Fully implemented status logic according to specification table
- **Accurate days calculation**: Days Overdue field shows actual payment delays (positive for late, 0 for on-time/early)
- **Improved data layout**: Report headers positioned below metadata with proper formatting and borders

### Payment Matching Strategy
The system uses a sophisticated matching algorithm that handles:
- Exact amount matches between transactions and expected rental payments
- Duplicate amount detection with conflict resolution
- Date-based search windows (7 days before expected date)
- Grace periods before marking payments overdue (3 days)
- **Enhanced fallback search** across entire statement period when narrow window fails
- **Automatic payment period detection** from bank statement text patterns

### Russian Localization System (August 2025)
Full implementation of Russian language support:
- **Complete Russian translations**: Created messages_ru.json with 42 localized messages covering all UI elements
- **CLI language switching**: Added --lang/--language option supporting en/ru selection
- **Environment variable support**: GARAGE_TRACKER_LANG environment variable for default language setting
- **Runtime language switching**: LocalizationManager.switch_language() method for dynamic language changes
- **Comprehensive testing**: 12 unit tests covering all localization scenarios including error handling
- **Seamless integration**: All CLI output, Excel reports, and error messages properly localized
- **Result**: Full bilingual support - users can work in English or Russian with identical functionality

### Enhanced Matching Logic (January 2025)
Two-tier matching system for maximum payment detection:
1. **Primary Match**: Standard 7-day window around expected payment date
2. **Fallback Match**: When primary fails, searches entire statement period by amount only
   - Prioritizes earliest transaction when multiple matches found
   - Provides detailed notes about wide search matches
   - Improved coverage from 46.7% to 66.7% in real data testing

### Automatic Period Detection
Innovative feature that extracts payment analysis periods directly from bank statements:
- Searches for period patterns like "Итого по операциям с 01.05.2025 по 12.06.2025"
- Automatically determines the correct analysis month (typically the start month)
- Eliminates manual date configuration errors
- Ensures analysis accuracy by using bank-provided period information
- Currently supports Sberbank statement format with extensible design for other banks

### Date Handling Fixes (August 2025)
Critical fixes to ensure proper date handling throughout the system:
- **Analysis Date Correction**: CLI option 3 now correctly uses detected period end date instead of current date
- **Expected Date Separation**: PaymentMatcher now properly separates target month (for expected date calculation) from analysis date (for status determination)
- **Payment Period Integration**: Expected dates now correctly calculated from payment period's target month rather than analysis date month
- **Transaction Filtering Fix**: Analysis date now properly filters transactions - only payments made on or before analysis date are considered for matching
- **Result**: Analysis date correctly affects payment detection (e.g., 8 received at 2025-05-25 vs 10 received at 2025-06-12)

### Days Overdue Calculation Fix (August 2025)
Final correction to Days Overdue logic to match user requirements:
- **Received Payments**: Days Overdue = Actual Date - Expected Date (can be negative for early payments)
- **Overdue Payments**: Days Overdue = Analysis Date - Expected Date (always positive for overdue)
- **PaymentMatcher Fix**: Removed max(0, days_difference) constraint that prevented negative values
- **StatusDeterminer Integration**: Proper calculation delegation for all payment types (Received, Overdue, Pending)
- **Pending Status Fix**: Added PENDING to ExcelWriter display conditions so Days Overdue shows for pending payments
- **Excel Display**: Received, Overdue, and Pending statuses now show accurate Days Overdue values
- **Result**: Early payments show negative values (-1, -2), late payments show positive values, overdue and pending calculations use analysis date

### Parser Architecture
Implements a factory pattern for handling different bank statement formats:
- Extensible parser system supporting multiple banks
- Currently includes Sberbank Excel statement parser
- Excel garage registry parser with flexible column mapping
- Interface-based design allows easy addition of new formats

### Status Determination
Comprehensive rule-based system for payment status classification according to specification:
- **RECEIVED**: Payment found within acceptable window [expected_date - 7 days; expected_date + 3 days]
- **OVERDUE**: Current date > expected_date + 3 days AND no payment found
- **PENDING**: Expected_date ≤ current_date ≤ expected_date + 3 days AND no payment found  
- **NOT_DUE**: Current date < expected_date (payment time hasn't arrived)
- **UNCLEAR**: Multiple matching payments found or payments outside acceptable window

### Configuration Management
YAML-based configuration system supporting:
- Multi-language support (English/Russian)
- Configurable matching parameters
- Parser-specific settings
- Environment-based overrides

## Data Models

### Core Entities
- **Garage**: Immutable value object representing rental unit with ID, monthly rent, start date, and payment day
- **Transaction**: Bank statement entry with date, amount, category, and source tracking
- **Payment**: Represents expected vs actual payment with status and metadata
- **Report**: Aggregates payment data with summary statistics and analysis
- **PaymentPeriod**: New value object representing extracted payment period from bank statements with start/end dates and source text

### Validation Strategy
Comprehensive validation at model boundaries:
- Domain models enforce business rules in constructors
- Parsers validate file formats and data integrity
- Use cases validate request parameters
- Exception hierarchy provides specific error handling

# External Dependencies

## Core Dependencies
- **openpyxl**: Excel file reading and writing for garage registries and bank statements
- **click**: Command-line interface framework for user interaction
- **pyyaml**: Configuration file parsing and management
- **pathlib**: Modern file path handling throughout the application

## Development Dependencies
- **pytest**: Unit and integration testing framework
- **unittest.mock**: Mocking for isolated unit tests
- **tempfile**: Temporary file handling for test scenarios

## File Format Support
- **Input**: Excel files (.xlsx, .xls) for garage registries and bank statements
- **Output**: Excel reports with formatted sheets, summary statistics, and payment details
- **Configuration**: YAML files for application settings and parser rules

## Future Integrations
The architecture supports planned additions:
- Database storage (designed to work with Drizzle ORM)
- Web interface components
- Additional bank statement formats
- Real-time notification systems
- Cloud storage integrations

## Localization System
Built-in internationalization support:
- JSON message files for different languages
- Fallback mechanism to English for missing translations
- Runtime language switching capability
- Localized report generation and error messages