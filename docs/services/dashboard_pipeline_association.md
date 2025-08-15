# Dashboard Pipeline Association Service

The Dashboard Pipeline Association service manages the relationships between dashboards and pipelines, enabling data visualization for pipeline outputs.

---

## Overview

The Dashboard Pipeline Association service provides functionality to link dashboards with specific pipelines, allowing users to visualize pipeline results and monitor data transformations through interactive dashboards.

---

## Service: DashboardPipelineAssociationService

### Key Methods
- **`create_association(dashboard_id, pipeline_id)`**: Creates a new association between a dashboard and pipeline
- **`get_associations_by_dashboard(dashboard_id)`**: Retrieves all pipelines associated with a specific dashboard
- **`get_associations_by_pipeline(pipeline_id)`**: Retrieves all dashboards associated with a specific pipeline
- **`delete_association(association_id)`**: Removes an association between a dashboard and pipeline
- **`update_association(association_id, dashboard_id, pipeline_id)`**: Updates an existing association

---

## Functionality

### Association Management
- **Create Associations**: Link dashboards with pipelines for data visualization
- **Retrieve Associations**: Query associations by dashboard or pipeline
- **Update Associations**: Modify existing dashboard-pipeline relationships
- **Delete Associations**: Remove dashboard-pipeline links

