# Contributing to WPS Toolkit

Thank you for considering contributing to the WPS Penetration Testing Toolkit! This document provides guidelines for contributing to the project.

## Code of Conduct

### Ethics First

This project is for **educational and authorized testing purposes only**. All contributions must:
- Not encourage or facilitate illegal activity
- Include appropriate warnings about legal restrictions
- Focus on defensive security and research
- Respect responsible disclosure principles

## Development Setup

### Prerequisites

- Python 3.9 or higher
- Git
- Basic understanding of WPS protocol (for core contributions)

### Setup Steps

```bash
# Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/FARHAN-Shot.git
cd FARHAN-Shot

# Install dependencies
pip install -r requirements.txt

# Run tests to verify setup
make test
```

## Coding Standards

### Python Style Guide

We follow **PEP 8** with the following additional requirements:

#### Type Hints
- **Required** for all function signatures
- Use `typing` module for complex types
- Example:
  ```python
  from typing import List, Optional, Dict, Any
  
  def process_data(items: List[str], config: Optional[Dict[str, Any]] = None) -> bool:
      """Process items with optional configuration."""
      pass
  ```

#### Documentation
- **Required** docstrings for all public functions, classes, and modules
- Use Google-style docstrings:
  ```python
  def calculate_checksum(pin: str) -> str:
      """
      Compute WPS PIN checksum digit.
      
      Args:
          pin: 7-digit PIN string
      
      Returns:
          Complete 8-digit PIN with checksum
      
      Raises:
          ValueError: If PIN is not 7 digits
      """
      pass
  ```

#### Code Structure
- **Maximum function length**: 80 lines
- **Single Responsibility Principle**: Each function does one thing
- **No magic numbers**: Use named constants
- **Clear variable names**: `ap_record` not `apr`

#### Error Handling
- Use specific exception types
- No bare `except:` clauses
- Provide meaningful error messages
- Example:
  ```python
  try:
      data = json.load(f)
  except json.JSONDecodeError as e:
      raise ValueError(f"Invalid JSON in {filename}: {e}")
  except FileNotFoundError:
      return None  # Expected case
  ```

### Code Organization

```python
# 1. Standard library imports
import json
import re
from pathlib import Path

# 2. Third-party imports
import pytest
from colorama import Fore

# 3. Local imports
from src.logger import get_logger
from src.ui import get_ui
```

## Testing Requirements

### Test Coverage
- **Minimum 80% coverage** for core modules
- **Required tests** for:
  - All public functions
  - Edge cases and error conditions
  - Parsing logic (regex patterns)
  - Database operations

### Writing Tests

```python
import pytest
from src.pingen import PINGenerator

class TestPINGenerator:
    """Test PIN generation functionality."""
    
    def test_checksum_calculation(self):
        """Test WPS PIN checksum calculation."""
        assert PINGenerator.compute_checksum('1234567') == '12345670'
    
    def test_invalid_input(self):
        """Test handling of invalid input."""
        with pytest.raises(ValueError):
            PINGenerator.compute_checksum('123')  # Too short
```

### Running Tests

```bash
# Run all tests
make test

# Run specific test file
pytest tests/test_pingen.py -v

# Run with coverage
pytest --cov=src --cov-report=html
```

## Git Workflow

### Branching Strategy

- `main`: Production-ready code
- `develop`: Integration branch for features
- `feature/name`: New features
- `fix/name`: Bug fixes
- `docs/name`: Documentation updates

### Commit Messages

Follow conventional commits format:

```
type(scope): short description

Longer description if needed

- Bullet points for details
- Reference issues: #123
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `refactor`: Code restructure (no behavior change)
- `docs`: Documentation only
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `style`: Formatting changes

**Examples:**
```
feat(pingen): implement vendor-pattern score-based pin ordering

- Add probability scoring system
- Implement prefix optimization
- Sort candidates by likelihood
- Fixes #42

fix(pixie): robust parsing for E-Hash1/E-Hash2/Nonce/PKE/PKR outputs

- Add comprehensive regex patterns
- Handle multiple output formats
- Test with real-world samples
```

### Pull Request Process

1. **Create feature branch** from `develop`
2. **Write code** following style guidelines
3. **Add tests** with 80%+ coverage
4. **Update documentation** if needed
5. **Run tests**: `make test`
6. **Commit changes** with conventional commits
7. **Open Pull Request** against `develop`

### PR Checklist

- [ ] Code follows style guidelines (PEP 8 + type hints)
- [ ] All new code has docstrings
- [ ] Tests added for new functionality
- [ ] All tests pass (`make test`)
- [ ] Documentation updated (README, docstrings)
- [ ] No dangerous live attack tests included
- [ ] Backward-compatible log/error messages preserved
- [ ] Simulation/dry-run mode tested

## Adding New Features

### 1. Propose the Feature
Open an issue describing:
- What problem it solves
- How it works
- Any security/legal considerations

### 2. Design Review
Discuss:
- Architecture changes
- API design
- Database schema updates
- Backward compatibility

### 3. Implementation
- Follow modular architecture
- Add to appropriate `src/` module
- Create unit tests
- Update documentation

### 4. Testing
- Write simulation tests (dry-run mode)
- No tests requiring root or actual hardware
- Use fixtures for realistic test data

## Module-Specific Guidelines

### Scanner Module (`src/scanner.py`)
- Must support dry-run simulation
- Parse multiple scanning backends (iw, iwlist, wpa_cli)
- Handle missing tools gracefully

### PIN Generation (`src/pingen.py`)
- All PINs must have valid checksums
- No duplicate PINs in output
- Document probability scoring logic
- Add tests for new patterns

### Database (`src/db.py`)
- Support both JSON and SQLite
- Maintain schema compatibility
- Add migration scripts for schema changes

### Pixie Dust (`src/pixie.py`)
- Must preserve backward-compatible output
- Support multiple pixiewps versions
- Comprehensive regex testing with fixtures

## Documentation

### README Updates
- Add new features to feature list
- Update usage examples
- Document new CLI flags
- Update project structure if changed

### Inline Documentation
```python
def complex_algorithm(data: List[int]) -> Dict[str, Any]:
    """
    Brief one-line description.
    
    Longer explanation of what this does, why it exists,
    and any important implementation details.
    
    Args:
        data: Description of parameter
    
    Returns:
        Description of return value
    
    Raises:
        ValueError: When data is invalid
    
    Example:
        >>> complex_algorithm([1, 2, 3])
        {'result': 6}
    """
    # Explain complex logic with inline comments
    pass
```

## Security Considerations

### What to Avoid
- **No actual attack code** against live networks in tests
- **No hardcoded credentials** or API keys
- **No instructions** for illegal use
- **No removing ethics warnings**

### What to Include
- Dry-run/simulation modes for all features
- Clear documentation of legal restrictions
- Responsible disclosure practices
- Educational context for features

## Questions?

- Open an issue for feature discussion
- Join discussions in existing issues
- Review closed PRs for examples

## Recognition

Contributors will be acknowledged in:
- README.md credits section
- Release notes
- Individual commit history

Thank you for helping make this project better! 🙏
