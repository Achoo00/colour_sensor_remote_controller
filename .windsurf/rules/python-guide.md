---
trigger: always_on
---

# Python Best Practices for Cascade

## 1. Code Style & Formatting
- **Indentation**: Use 4 spaces per level (no tabs)
- **Line Length**: Limit to 79 characters (72 for docstrings/comments)
- **Imports**: Group in this order with blank lines between:
  ```python
  # Standard library
  import os
  import sys
  from typing import List, Dict

  # Third-party
  import requests
  from flask import Flask

  # Local application
  from . import utils
  from .models import User
  ```

## 2. Naming Conventions
- **Modules/Packages**: `lowercase_with_underscores`
- **Classes**: `PascalCase`
- **Functions/Methods**: `snake_case()`
- **Variables**: `snake_case`
- **Constants**: `UPPER_CASE`
- **Private**: `_private_var` (single underscore)
- **Name Mangling**: `__mangled_name` (double underscore)

## 3. Documentation
- **Docstrings**: Use triple-double quotes (Google or NumPy style)
  ```python
  def calculate_average(numbers: List[float]) -> float:
      """Calculate the arithmetic mean of a list of numbers.

      Args:
          numbers: List of numbers to average

      Returns:
          float: The arithmetic mean

      Raises:
          ValueError: If numbers is empty
      """
  ```
- **Type Hints**: Always use type hints for function signatures
- **Comments**: Explain "why" not "what"

## 4. Error Handling
- Be specific with exceptions
- Use custom exceptions for domain-specific errors
- Include context in error messages
  ```python
  try:
      value = my_dict[key]
  except KeyError as e:
      raise KeyError(f"Key {key} not found in configuration") from e
  ```

## 5. Project Structure
```
project/
├── src/
│   └── package_name/
│       ├── __init__.py
│       ├── module1.py
│       └── subpackage/
├── tests/
│   ├── __init__.py
│   └── test_module1.py
├── docs/
├── .gitignore
├── pyproject.toml
├── README.md
└── requirements-dev.txt
```

## 6. Testing
- Write unit tests for all public functions/methods
- Use descriptive test names
- Follow Arrange-Act-Assert pattern
  ```python
  def test_calculate_average_empty_list():
      # Arrange
      numbers = []
      
      # Act/Assert
      with pytest.raises(ValueError):
          calculate_average(numbers)
  ```

## 7. Tooling
- **Formatting**: Black
- **Linting**: Ruff or flake8
- **Type Checking**: mypy
- **Testing**: pytest
- **Dependencies**: Use `pyproject.toml` with `[project]` section

## 8. Performance
- Use list comprehensions over loops when appropriate
- Prefer `f-strings` for string formatting
- Use `pathlib` for file paths
- Consider generators for large datasets

## 9. Security
- Never hardcode secrets - use environment variables
- Use `secrets` module for cryptographic operations
- Sanitize all user inputs

## 10. Git Practices
- Write clear, concise commit messages
- Use feature branches
- Keep commits atomic
- Use pull requests for code review

## 11. Logging
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
```

## 12. Virtual Environments
Always use virtual environments:
```bash
# Create
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"
```

## 13. Type Hints Example
```python
from typing import List, Optional, Dict, Union, Tuple

def process_data(
    data: List[Dict[str, Union[str, int]]],
    config: Optional[Dict[str, str]] = None
) -> Tuple[bool, int]:
    """Process data with optional configuration."""
    ...
```

## 14. Context Managers
```python
with open('file.txt', 'r') as f:
    data = f.read()

# For custom resources
class DatabaseConnection:
    def __enter__(self):
        self.conn = create_connection()
        return self.conn
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()
```

## 15. List/Dict Comprehensions
```python
# Good
squares = [x**2 for x in range(10) if x % 2 == 0]

# Avoid nesting too much
matrix = [[1, 2], [3, 4]]
flat = [x for row in matrix for x in row]  # OK
```

## 16. Error Messages
```python
# Bad
raise ValueError("Invalid input")

# Good
raise ValueError(
    f"Expected positive integer, got {value} "
    f"(type: {type(value).__name__})"
)
```

## 17. Configuration
Use environment variables with defaults:
```python
import os
from typing import Optional

def get_config(key: str, default: Optional[str] = None) -> str:
    """Get configuration from environment variables."""
    value = os.getenv(key, default)
    if value is None:
        raise ValueError(f"Missing required configuration: {key}")
    return value
```

## 18. Dependencies
- Pin all dependencies with exact versions
- Separate dev dependencies
- Use `pyproject.toml` for modern projects

## 19. Performance Tips
- Use `set` for membership testing
- Use `collections.defaultdict` for default values
- Prefer `join()` for string concatenation in loops

## 20. Code Review Checklist
- [ ] Code follows style guide
- [ ] Type hints are present
- [ ] Tests are included
- [ ] Documentation is updated
- [ ] Error handling is appropriate
- [ ] No commented-out code
- [ ] Performance considerations addressed

This markdown document provides a comprehensive set of best practices that can be followed when working with Python code in Cascade. The formatting uses proper markdown structure with code blocks and sections for easy reference.