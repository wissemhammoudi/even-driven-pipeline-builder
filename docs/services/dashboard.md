# Dashboard Service

This module provides logic for aggregating and presenting dashboard statistics, charts, and recent pipeline activity for users and administrators.

---

## Main Class

### DashboardService
Aggregates pipeline and run statistics, recent activity, and chart data for dashboard views.

**Key Methods:**
- `__init__(self)`: Initializes the dashboard repository.
- `get_dashboard_data_by_pipeline_ids(self, pipeline_ids)`: Returns a dictionary with stats, charts, and recent pipelines for the given pipeline IDs.
- `get_dashboard_stats_by_pipeline_ids(self, pipeline_ids)`: Returns pipeline and run statistics for the given pipeline IDs.
- `get_recent_pipelines_by_pipeline_ids(self, limit=5, pipeline_ids=None)`: Returns a list of recent pipelines for the given pipeline IDs.
- `get_charts_data_by_pipeline_ids(self, days=30, pipeline_ids=None)`: Returns chart data (creation trend, status distribution, success/failure) for the given pipeline IDs and time window.

---

Use this module to:
- Power dashboard views with up-to-date pipeline and run statistics.
- Provide users and admins with insights into pipeline activity and health.
- Support charting and reporting features in your data platform. 