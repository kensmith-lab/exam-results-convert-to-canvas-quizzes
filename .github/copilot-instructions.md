# AI Agent Instructions for exam-results-convert-to-canvas-quizzes

## Project Overview
This project converts exam results data into Canvas quiz format. The tool processes exam results and transforms them into Canvas-compatible quiz structures for educational platforms.

## Key Architecture Concepts

### Data Flow
- **Input**: Exam results data (likely CSV, JSON, or Excel formats)
- **Processing**: Parse, validate, and transform exam data 
- **Output**: Canvas-compatible quiz format (QTI or Canvas native format)

### Expected Components
- **Data Parser**: Handles various input formats (CSV, JSON, Excel)
- **Canvas API Integration**: For direct upload to Canvas or QTI export
- **Validation Engine**: Ensures data integrity and Canvas compatibility
- **Configuration**: Settings for quiz parameters, grading scales, etc.

## Development Guidelines

### File Organization
- Place parsers in `src/parsers/` or similar
- Canvas integration code in `src/canvas/` 
- Configuration files in `config/`
- Sample data and templates in `data/` or `examples/`
- Documentation in `docs/` or maintain in `documents/` folder

### Data Handling Patterns
- Use robust CSV/Excel parsing (consider pandas for Python, csv-parser for Node.js)
- Implement proper error handling for malformed input data
- Validate Canvas quiz format requirements before output
- Support batch processing for multiple exam files

### Canvas Integration
- Follow Canvas API rate limiting and authentication patterns
- Support both Canvas native format and QTI 1.2/2.1 standards
- Handle Canvas course/quiz metadata properly
- Consider Canvas question types: multiple choice, essay, fill-in-blank, etc.

### Configuration Management
- Support configurable field mappings (student IDs, question formats)
- Allow customizable grading scales and quiz settings
- Enable template-based quiz creation

## Testing Approach
- Unit tests for each parser and transformation function
- Integration tests with sample Canvas quiz data
- Test edge cases: missing data, malformed files, Unicode characters
- Validate output against Canvas import requirements

## Key Dependencies to Consider
- **Python**: pandas, requests, openpyxl, lxml (for QTI)
- **Node.js**: csv-parser, xlsx, canvas-api, xml2js
- Canvas LTI/API libraries depending on integration approach

## Common Pitfalls
- Canvas has specific requirements for question IDs and metadata
- Time zones and date formatting can cause import issues
- Student identifier matching between systems
- Quiz question type limitations in Canvas

## Development Workflow
Since this is an early-stage project:
1. Start with a simple CLI tool or script
2. Focus on one input format initially (likely CSV)
3. Create sample data files for testing
4. Build incrementally: parse → transform → output
5. Add Canvas integration after core transformation works

## External Resources
- Canvas API Documentation: https://canvas.instructure.com/doc/api/
- QTI Specification: https://www.imsglobal.org/question/
- Canvas Quiz Import Format documentation