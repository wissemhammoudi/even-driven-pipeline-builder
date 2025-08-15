# SQL String Validator

The SQL String Validator provides SQL syntax validation and auto-fixing capabilities using SQLFluff.

---

## Overview

The `SQLValidator` class validates SQL strings for syntax correctness and can automatically fix common SQL formatting issues. It's built on top of SQLFluff, a powerful SQL linting and formatting tool.

---

## Class: SQLValidator

### Initialization
```python
def __init__(
    self,
    dialect: str = "ansi",
    rules: Optional[List[str]] = None,
    exclude_rules: Optional[List[str]] = None,
    config: Optional[Dict[str, Union[str, bool, List[str]]]] = None
):
```

**Parameters:**
- **`dialect`**: SQL dialect (default: "ansi")
- **`rules`**: Specific rules to enforce
- **`exclude_rules`**: Rules to exclude from validation
- **`config`**: Additional SQLFluff configuration options

---

## Key Methods

### validate
```python
def validate(self, sql_text: str, fix: bool = False) -> Dict:
```

**Parameters:**
- **`sql_text`**: SQL string to validate
- **`fix`**: Whether to attempt auto-fixing (default: False)

**Returns:**
- **`valid`**: Boolean indicating if SQL is valid
- **`violations`**: List of validation violations
- **`fixed_sql`**: Auto-fixed SQL string (if fix=True)

