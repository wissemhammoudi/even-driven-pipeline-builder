import sqlfluff
from typing import Dict, Union, List, Optional

class SQLValidator:    
    def __init__(
        self,
        dialect: str = "ansi",
        rules: Optional[List[str]] = None,
        exclude_rules: Optional[List[str]] = None,
        config: Optional[Dict[str, Union[str, bool, List[str]]]] = None
    ):
        """
        Initialize the SQL validator with configuration options.
        
        Args:
            dialect: SQL dialect to use (e.g., 'ansi', 'postgres', 'snowflake', etc.)
            rules: Specific rules to enforce (None for all rules)
            exclude_rules: Rules to exclude from validation
            config: Additional SQLFluff configuration options
        """
        self.dialect = dialect
        self.rules = rules
        self.exclude_rules = exclude_rules
        
        self.config = {
            "dialect": self.dialect,
            "rules": self.rules,
            "exclude_rules": self.exclude_rules,
        }
        
        if config:
            self.config.update(config)
    
    def validate(
        self,
        sql_text: str,
        fix: bool = False
    ) -> Dict[str, Union[bool, List[Dict[str, Union[str, int]]], str]]:
        result = {
            "valid": True,
            "violations": [],
            "fixed_sql": None
        }
        
        try:
            lint_result = sqlfluff.lint(
                sql_text,
                dialect=self.dialect,
                rules=self.rules,
                exclude_rules=self.exclude_rules
            )
            
            if lint_result:
                result["valid"] = False
                result["violations"] = lint_result
                
                if fix:
                    try:
                        fix_result = sqlfluff.fix(
                            sql_text,
                            dialect=self.dialect,
                            rules=self.rules,
                            exclude_rules=self.exclude_rules
                        )
                        if fix_result != sql_text:
                            result["fixed_sql"] = fix_result
                            new_lint_result = sqlfluff.lint(
                                fix_result,
                                dialect=self.dialect,
                                rules=self.rules,
                                exclude_rules=self.exclude_rules
                            )
                            result["valid"] = not bool(new_lint_result)
                            if new_lint_result:
                                result["violations"] = new_lint_result
                    except Exception as fix_e:
                        result["valid"] = False
                        result["violations"] = [{
                            "description": f"SQLFluff parsing error and fix failed: {str(e)}; Fix error: {str(fix_e)}",
                            "line_no": 1,
                            "line_pos": 1,
                            "code": "PARSE_AND_FIX_ERROR"
                        }]
        
        except Exception as e:
            result["valid"] = False
            result["violations"] = [{
                "description": f"SQLFluff parsing error: {str(e)}",
                "line_no": 1,
                "line_pos": 1,
                "code": "PARSE_ERROR"
            }]
        
        return result

validate = SQLValidator()
