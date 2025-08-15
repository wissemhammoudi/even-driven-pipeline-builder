export const StepTypeEnum = {
  DATA_INGESTION: 'data ingestion',
  DATA_TRANSFORMATION: 'data transformation',
  DATA_VISUALIZATION: 'data visualization'
}

export const ToolEnum = {
  DLT: 'dlt',
  MELTANO: 'meltano',
  DBT: 'dbt',
  SQLMESH: 'sqlmesh',
  SUPERSET: 'superset'
}

export function getStepTitle (formDataType, step) {
  if (formDataType === StepTypeEnum.DATA_TRANSFORMATION) {
    switch (step) {
      case 1:
        return 'Basic Information'
      case 2:
        return 'Utility Type Selection'
      case 3:
        return 'Transformation Configuration'
      case 4:
        return 'Review & Save'
      default:
        return ''
    }
  } else if (formDataType === StepTypeEnum.DATA_VISUALIZATION) {
    switch (step) {
      case 1:
        return 'Basic Information'
      case 2:
        return 'Connection Configuration'
      case 3:
        return 'Review & Save'
      default:
        return ''
    }
  } else {
    switch (step) {
      case 1:
        return 'Basic Information'
      case 2:
        return 'Source Configuration'
      case 3:
        return 'Destination Configuration'
      case 4:
        return 'Table Selection'
      case 5:
        return 'Review & Save'
      default:
        return ''
    }
  }
}

export function getStepDescription (formDataType, step) {
  if (formDataType === StepTypeEnum.DATA_TRANSFORMATION) {
    switch (step) {
      case 1:
        return 'Enter basic information about your transformation step'
      case 2:
        return 'Select the transformation utility (e.g., dbt, sqlmesh)'
      case 3:
        return 'Configure column transformations, joins, and agentic transformations'
      case 4:
        return 'Review and save your transformation step'
      default:
        return ''
    }
  } else if (formDataType === StepTypeEnum.DATA_VISUALIZATION) {
    switch (step) {
      case 1:
        return 'Enter basic information about your visualization step'
      case 2:
        return 'Configure database connection for Superset'
      case 3:
        return 'Review and save your visualization step'
      default:
        return ''
    }
  } else {
    switch (step) {
      case 1:
        return 'Enter basic information about your ingestion step'
      case 2:
        return 'Configure source database connection'
      case 3:
        return 'Configure destination database connection'
      case 4:
        return 'Select tables to ingest'
      case 5:
        return 'Review and save your ingestion step'
      default:
        return ''
    }
  }
}
