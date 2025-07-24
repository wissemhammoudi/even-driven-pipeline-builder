{# Null Value Transformations #}
{% macro handle_null_value_transformation(column_name, schema_name, table_name, value) %}
  {% if value and value|lower in ("avg", "sum", "min", "max", "count", "median") %}
    {% set agg_func = value|upper %}
    COALESCE(
      {{ column_name }},
      (
        SELECT {{ agg_func }}({{ column_name }})
        FROM {{ schema_name }}.{{ table_name }}
        WHERE {{ column_name }} IS NOT NULL
      )
    )
  {% else %}
    {{ column_name }}
  {% endif %}
{% endmacro %}


{# Window Function Transformations #}
{% macro handle_window_function_transformation(column_name, value) %}
  {% if value %}
    {% set parts = value.split(":") %}
    {% set func_type = parts[0] %}
    {% set partition_by = parts[1] if parts|length > 1 else "" %}
    {% set order_by = parts[2] if parts|length > 2 else "" %}

    {% if func_type in ("row_number", "rank", "dense_rank") %}
      {{ func_type|upper }}() OVER (
        {% if partition_by %}PARTITION BY {{ partition_by }}{% endif %}
        {% if order_by %}ORDER BY {{ order_by }}{% endif %}
      )
    {% elif func_type in ("lag", "lead") %}
      {% set offset = parts[3] if parts|length > 3 else "1" %}
      {% set default_val = parts[4] if parts|length > 4 else "NULL" %}
      {{ func_type|upper }}({{ column_name }}, {{ offset }}, {{ default_val }}) OVER (
        {% if partition_by %}PARTITION BY {{ partition_by }}{% endif %}
        {% if order_by %}ORDER BY {{ order_by }}{% endif %}
      )
    {% elif func_type in ("sum", "avg", "min", "max", "count") %}
      {{ func_type|upper }}({{ column_name }}) OVER (
        {% if partition_by %}PARTITION BY {{ partition_by }}{% endif %}
        {% if order_by %}ORDER BY {{ order_by }}{% endif %}
      )
    {% else %}
      {{ column_name }}
    {% endif %}
  {% else %}
    {{ column_name }}
  {% endif %}
{% endmacro %}

{# String Transformations #}
{% macro handle_string_transformation(column_name, value) %}
  {% if value %}
    {% set transform_type = value|lower %}
    {% if transform_type == "upper" %}
      UPPER({{ column_name }})
    {% elif transform_type == "lower" %}
      LOWER({{ column_name }})
    {% elif transform_type == "trim" %}
      TRIM({{ column_name }})
    {% elif transform_type == "length" %}
      LENGTH({{ column_name }})
    {% elif transform_type.startswith("substring") %}
      {% set parts = transform_type.split(":") %}
      {% set start_pos = parts[1] if parts|length > 1 else "1" %}
      {% set length = parts[2] if parts|length > 2 else "" %}
      {% if length %}
        SUBSTRING({{ column_name }}, {{ start_pos }}, {{ length }})
      {% else %}
        SUBSTRING({{ column_name }}, {{ start_pos }})
      {% endif %}
    {% elif transform_type.startswith("replace") %}
      {% set parts = transform_type.split(":") %}
      {% set old_value = parts[1] if parts|length > 1 else "" %}
      {% set new_value = parts[2] if parts|length > 2 else "" %}
      REPLACE({{ column_name }}, '{{ old_value }}', '{{ new_value }}')
    {% else %}
      {{ column_name }}
    {% endif %}
  {% else %}
    {{ column_name }}
  {% endif %}
{% endmacro %}

{# Date Transformations #}
{% macro handle_date_transformation(column_name, value) %}
  {% if value %}
    {% set transform_type = value|lower %}
    {% if transform_type == "extract_year" %}
      EXTRACT(YEAR FROM {{ column_name }})
    {% elif transform_type == "extract_month" %}
      EXTRACT(MONTH FROM {{ column_name }})
    {% elif transform_type == "extract_day" %}
      EXTRACT(DAY FROM {{ column_name }})
    {% elif transform_type == "date_trunc_month" %}
      DATE_TRUNC('month', {{ column_name }})
    {% elif transform_type == "date_trunc_quarter" %}
      DATE_TRUNC('quarter', {{ column_name }})
    {% elif transform_type == "date_trunc_year" %}
      DATE_TRUNC('year', {{ column_name }})
    {% elif transform_type == "age_in_days" %}
      DATE_DIFF('day', {{ column_name }}, CURRENT_DATE)
    {% elif transform_type == "format_iso" %}
      TO_CHAR({{ column_name }}, 'YYYY-MM-DD')
    {% else %}
      {{ column_name }}
    {% endif %}
  {% else %}
    {{ column_name }}
  {% endif %}
{% endmacro %}

{# Main Dispatcher Macro #}
{% macro handle_column_transformation(column_name, schema_name, table_name, action=None, value=None) %}
  {% if action == "null_value" %}
    {{ handle_null_value_transformation(column_name, schema_name, table_name, value) }}
  {% elif action == "window_function" %}
    {{ handle_window_function_transformation(column_name, value) }}
  {% elif action == "string_transform" %}
    {{ handle_string_transformation(column_name, value) }}
  {% elif action == "date_transform" %}
    {{ handle_date_transformation(column_name, value) }}
  {% else %}
    {{ column_name }}
  {% endif %}
{% endmacro %}