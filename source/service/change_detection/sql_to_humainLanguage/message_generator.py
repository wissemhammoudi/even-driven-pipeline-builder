import re
from typing import Dict, Any

class SchemaChangeMessageGenerator:

    @staticmethod
    def generate_human_readable_message(change_data: Dict[str, Any]) -> str:
        command_tag = change_data.get('command_tag', '').upper()
        object_identity = change_data.get('object_identity', '')
        command = change_data.get('command', '')
        schema_name = change_data.get('schema_name', '')
        
        table_name = object_identity.split('.')[-1] if '.' in object_identity else object_identity
        
        if command_tag == 'ALTER TABLE':
            return SchemaChangeMessageGenerator._parse_alter_table(command, table_name, schema_name)
        elif command_tag == 'CREATE TABLE':
            return SchemaChangeMessageGenerator._parse_create_table(command, table_name, schema_name)
        elif command_tag == 'DROP TABLE':
            return SchemaChangeMessageGenerator._parse_drop_table(command, table_name, schema_name)
        else:
            return f"Database schema change detected: {command_tag} operation on {object_identity}"
    
    @staticmethod
    def _parse_alter_table(command: str, table_name: str, schema_name: str) -> str:
        command_upper = command.upper()
        
        if 'DROP COLUMN' in command_upper:
            column_match = re.search(r'DROP COLUMN\s+(?:IF EXISTS\s+)?([^\s;]+)', command_upper)
            if column_match:
                column_name = column_match.group(1).strip('"').strip("'")
                return f"Column '{column_name}' was removed from table '{table_name}' in schema '{schema_name}'"
            return f"A column was removed from table '{table_name}' in schema '{schema_name}'"
        
        elif 'ADD COLUMN' in command_upper:
            column_match = re.search(r'ADD COLUMN\s+(?:IF NOT EXISTS\s+)?([^\s;]+)', command_upper)
            if column_match:
                column_name = column_match.group(1).strip('"').strip("'")
                return f"Column '{column_name}' was added to table '{table_name}' in schema '{schema_name}'"
            return f"A new column was added to table '{table_name}' in schema '{schema_name}'"
        
        elif 'RENAME COLUMN' in command_upper:
            rename_match = re.search(r'RENAME COLUMN\s+([^\s]+)\s+TO\s+([^\s;]+)', command_upper)
            if rename_match:
                old_name = rename_match.group(1).strip('"').strip("'")
                new_name = rename_match.group(2).strip('"').strip("'")
                return f"Column '{old_name}' was renamed to '{new_name}' in table '{table_name}' in schema '{schema_name}'"
            return f"A column was renamed in table '{table_name}' in schema '{schema_name}'"
        
        elif 'ALTER COLUMN' in command_upper and 'TYPE' in command_upper:
            column_match = re.search(r'ALTER COLUMN\s+([^\s]+)\s+TYPE\s+([^;]+)', command_upper)
            if column_match:
                column_name = column_match.group(1).strip('"').strip("'")
                new_type = column_match.group(2).strip()
                return f"Column '{column_name}' data type was changed to '{new_type}' in table '{table_name}' in schema '{schema_name}'"
            return f"A column data type was modified in table '{table_name}' in schema '{schema_name}'"
        
        elif 'RENAME TO' in command_upper:
            rename_match = re.search(r'RENAME TO\s+([^\s;]+)', command_upper)
            if rename_match:
                new_table_name = rename_match.group(1).strip('"').strip("'")
                return f"Table '{table_name}' was renamed to '{new_table_name}' in schema '{schema_name}'"
            return f"Table '{table_name}' was renamed in schema '{schema_name}'"
        
        elif 'ADD CONSTRAINT' in command_upper:
            constraint_match = re.search(r'ADD CONSTRAINT\s+([^\s]+)', command_upper)
            if constraint_match:
                constraint_name = constraint_match.group(1).strip('"').strip("'")
                return f"Constraint '{constraint_name}' was added to table '{table_name}' in schema '{schema_name}'"
            return f"A constraint was added to table '{table_name}' in schema '{schema_name}'"
        
        elif 'DROP CONSTRAINT' in command_upper:
            constraint_match = re.search(r'DROP CONSTRAINT\s+(?:IF EXISTS\s+)?([^\s;]+)', command_upper)
            if constraint_match:
                constraint_name = constraint_match.group(1).strip('"').strip("'")
                return f"Constraint '{constraint_name}' was removed from table '{table_name}' in schema '{schema_name}'"
            return f"A constraint was removed from table '{table_name}' in schema '{schema_name}'"
        
        else:
            return f"Table '{table_name}' structure was modified in schema '{schema_name}'"
    
    @staticmethod
    def _parse_create_table(command: str, table_name: str, schema_name: str) -> str:
        return f"New table '{table_name}' was created in schema '{schema_name}'"
    
    @staticmethod
    def _parse_drop_table(command: str, table_name: str, schema_name: str) -> str:
        return f"Table '{table_name}' was deleted from schema '{schema_name}'"
    
    @staticmethod
    def generate_detailed_message(change_data: Dict[str, Any], is_breaking: bool) -> str:
        basic_message = SchemaChangeMessageGenerator.generate_human_readable_message(change_data)
        
        if is_breaking:
            basic_message += "\n\n⚠️  WARNING: This is a breaking change that may affect your data pipeline!"
        
        return basic_message 