# Pipeline Dashboard Service

This module provides analytics and reporting for individual pipelines, supporting dashboard views and insights into pipeline performance over time.

---

## Main Class

### PipelineDashboardService
Fetches analytics data for pipelines to power dashboard visualizations and reporting.

**Key Methods:**
- `__init__(self)`: Initializes the pipeline dashboard repository and database connection.
- `get_pipeline_analytics(self, pipeline_id, days=30)`: Returns analytics data for a given pipeline over a specified number of days.

---

Use this module to:
- Retrieve analytics and performance metrics for pipelines.
- Support dashboard and reporting features in your data platform. 