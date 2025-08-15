import { StepTypeEnum, ToolEnum } from '../utils'

const DEFAULT_CONFIG = {
  config_ids: [],
  connection_config: { utility: {} },
  destination_config: {},
  table_sync_config: { tables: [] },
  column_functions: {},
  join_transformations: [],
  agentic_transformations: []
}

const DEFAULT_DESTINATION_CONFIG = {
  host: 'postgres_destination',
  port: 5432,
  database: 'mydatabase',
  database_name: 'mydatabase',
  user: 'user',
  password: 'password',
  schema: 'public',
  sqlalchemy_uri: 'postgresql+psycopg2://user:password@postgres_destination:5432/mydatabase'
}

function validateInput(formData) {
  if (!formData || typeof formData !== 'object') {
    throw new Error('formData must be a valid object')
  }
  
  if (!formData.type) {
    throw new Error('formData.type is required')
  }
  
  if (!formData.step_config || typeof formData.step_config !== 'object') {
    throw new Error('formData.step_config must be a valid object')
  }
}

function createBaseConfig(formData, configIds) {
  const baseConfig = {
    ...DEFAULT_CONFIG,
    ...formData.step_config,
    utility_type: formData.step_config.utility_type,
    connection_config: {
      ...DEFAULT_CONFIG.connection_config,
      ...formData.step_config.connection_config
    }
  }
  
  const formDataConfigIds = formData.step_config?.config_ids
  baseConfig.config_ids = (formDataConfigIds && formDataConfigIds.length > 0) ? formDataConfigIds : (configIds || [])
  
  return baseConfig
}

function setConfigType(stepConfig, stepType) {
  const configTypeMap = {
    [StepTypeEnum.DATA_TRANSFORMATION]: StepTypeEnum.DATA_TRANSFORMATION,
    [StepTypeEnum.DATA_VISUALIZATION]: StepTypeEnum.DATA_VISUALIZATION, 
    [StepTypeEnum.DATA_INGESTION]: StepTypeEnum.DATA_INGESTION
  }
  
  stepConfig.config_type = configTypeMap[stepType] || StepTypeEnum.DATA_INGESTION
  return stepConfig
}

function buildMeltanoTransformationConfig(stepConfig) {
  if (!stepConfig.utility_type) {
    stepConfig.utility_type = 'dbt-postgres'
  }
  return stepConfig
}

function buildSqlmeshTransformationConfig(stepConfig, allPipelineSteps) {
  stepConfig.dialect = stepConfig.dialect || 'postgres'
  
  const ingestionStep = allPipelineSteps?.find(step => step.type === StepTypeEnum.DATA_INGESTION)
  const ingestionConfig = ingestionStep?.step_config
  
  if (ingestionConfig) {
    stepConfig.source = ingestionConfig.source || 
                       ingestionConfig.extractor_type || 
                       'sql_database'
    
    stepConfig.destination = ingestionConfig.destination || 
                            ingestionConfig.loader_type || 
                            'postgres'
  } else {
    stepConfig.source = 'sql_database'
    stepConfig.destination = 'postgres'
  }
  
  return stepConfig
}

function buildTransformationConfig(stepConfig, allPipelineSteps, tableColumns) {
  if (stepConfig.tool === ToolEnum.MELTANO) {
    stepConfig = buildMeltanoTransformationConfig(stepConfig)
  } else if (stepConfig.tool === ToolEnum.SQLMESH) {
    stepConfig = buildSqlmeshTransformationConfig(stepConfig, allPipelineSteps)
  }

  if (!stepConfig.destination_config || Object.keys(stepConfig.destination_config).length === 0) {
    stepConfig.destination_config = buildDestinationConfigFromSteps(allPipelineSteps)
  }

  if (stepConfig.column_functions?.tables && Object.keys(stepConfig.column_functions.tables).length > 0) {
    stepConfig.table_sync_config = buildTransformationTableSyncConfig(stepConfig.column_functions, tableColumns)
  } else if (!stepConfig.table_sync_config || !stepConfig.table_sync_config.tables) {
    stepConfig.table_sync_config = buildTableSyncConfig(allPipelineSteps, tableColumns)
  }

  return stepConfig
}

function buildDestinationConfig(destConfig) {
  if (!destConfig.database_name) {
    destConfig.database_name = destConfig.database || destConfig.dbname || 'mydatabase'
  }

  if (!destConfig.sqlalchemy_uri && 
      destConfig.host && 
      destConfig.user && 
      destConfig.password && 
      destConfig.database_name) {
    const port = destConfig.port || 5432
    destConfig.sqlalchemy_uri = `postgresql+psycopg2://${destConfig.user}:${destConfig.password}@${destConfig.host}:${port}/${destConfig.database_name}`
  }

  if (!destConfig.schema) {
    destConfig.schema = 'public'
  }

  return destConfig
}

function buildVisualizationConfig(stepConfig) {
  if (stepConfig.destination_config && Object.keys(stepConfig.destination_config).length > 0) {
    stepConfig.destination_config = buildDestinationConfig(stepConfig.destination_config)
  } else {
    stepConfig.destination_config = { ...DEFAULT_DESTINATION_CONFIG }
  }

  if (!stepConfig.utility_type) {
    stepConfig.utility_type = ToolEnum.SUPERSET
  }

  return stepConfig
}

function createTableSyncMap(selectedTables, tableColumns) {
  const tableSyncMap = {}
  
  Array.from(selectedTables).forEach(tableName => {
    const columns = tableColumns[tableName] || []
    const selectedColumns = columns
      .filter(col => col.selected)
      .map(col => col.column_name || col.column)
    
    tableSyncMap[tableName] = {
      table_name: tableName,
      columns: selectedColumns.length > 0 ? selectedColumns : undefined
    }
  })
  
  return tableSyncMap
}

function buildDltTableSyncConfig(selectedTables) {
  return Array.from(selectedTables)
}

function buildMeltanoTableSyncConfig(selectedTables, tableColumns) {
  const tableSyncConfig = {}
  
  Array.from(selectedTables).forEach(tableName => {
    const columns = tableColumns[tableName] || []
    const selectedColumns = columns
      .filter(col => col.selected)
      .map(col => col.column_name || col.column)
    
    tableSyncConfig[tableName] = selectedColumns.map(col => ({
      column: col
    }))
  })
  
  return tableSyncConfig
}

function buildIngestionConfig(stepConfig, tableColumns, selectedTables) {
  if (selectedTables.size === 0) {
    return stepConfig
  }

  stepConfig.table_sync_map = createTableSyncMap(selectedTables, tableColumns)

  if (stepConfig.tool === ToolEnum.DLT) {
    stepConfig.table_sync_config = buildDltTableSyncConfig(selectedTables)
  } else if (stepConfig.tool === ToolEnum.MELTANO) {
    stepConfig.table_sync_config = buildMeltanoTableSyncConfig(selectedTables, tableColumns)
  }

  return stepConfig
}

function extractDestinationFromTransformationStep(allPipelineSteps) {
  const transformationStep = allPipelineSteps?.find(step => step.type === StepTypeEnum.DATA_TRANSFORMATION)
  const destConfig = transformationStep?.step_config?.destination_config
  
  if (destConfig && destConfig.host && (destConfig.database || destConfig.dbname)) {
    return {
      host: destConfig.host,
      port: destConfig.port || 5432,
      database: destConfig.database || destConfig.dbname,
      database_name: destConfig.database || destConfig.dbname,
      user: destConfig.user || destConfig.username,
      password: destConfig.password,
      schema: destConfig.schema || 'public'
    }
  }
  
  return null
}

function extractDestinationFromIngestionStep(allPipelineSteps) {
  const ingestionStep = allPipelineSteps?.find(step => step.type === StepTypeEnum.DATA_INGESTION)
  const connectionConfig = ingestionStep?.step_config?.connection_config
  
  if (!connectionConfig) {
    return null
  }

  let destConfig = null
  const tool = ingestionStep.step_config.tool

  if (tool === ToolEnum.MELTANO) {
    destConfig = connectionConfig.loader
  } else if (tool === ToolEnum.DLT) {
    destConfig = connectionConfig.destination
  } else {
    destConfig = connectionConfig.loader || connectionConfig.destination
  }

  if (destConfig && destConfig.host) {
    return {
      host: destConfig.host,
      port: destConfig.port || 5432,
      database: destConfig.database || destConfig.dbname,
      database_name: destConfig.database || destConfig.dbname,
      user: destConfig.user || destConfig.username,
      password: destConfig.password,
      schema: destConfig.schema || destConfig.target_schema || 'public'
    }
  }
  
  return null
}

function buildDestinationConfigFromSteps(allPipelineSteps) {
  return extractDestinationFromTransformationStep(allPipelineSteps) || 
         extractDestinationFromIngestionStep(allPipelineSteps) || 
         null
}

function createTableConfig(tableName, columns) {
  const columnNames = columns
    .map(col => col.column || col.column_name)
    .filter(Boolean)
  
  return {
    schema_name: 'public',
    table_name: tableName,
    pk: ['id'],
    incremental_col: 'id',
    columns: columnNames.join(',')
  }
}

function buildTableSyncConfigFromArray(tableSyncConfig, tableColumns) {
  return {
    tables: tableSyncConfig.map(tableName => 
      createTableConfig(tableName, tableColumns[tableName] || [])
    )
  }
}

function buildTableSyncConfigFromObject(tableSyncConfig, tableColumns) {
  if (tableSyncConfig.tables) {
    return tableSyncConfig
  }
  
  const tableNames = Object.keys(tableSyncConfig)
  return {
    tables: tableNames.map(tableName => 
      createTableConfig(tableName, tableColumns[tableName] || [])
    )
  }
}

function buildTransformationTableSyncConfig(columnFunctions, tableColumns) {
  const tables = []
  
  console.log('buildTransformationTableSyncConfig called with:', { columnFunctions, tableColumns })
  
  const columnFunctionsTables = columnFunctions.tables || columnFunctions
  
  Object.keys(columnFunctionsTables).forEach(tableName => {
    let columnNames = []
    
    if (tableColumns[tableName] && tableColumns[tableName].length > 0) {
      columnNames = tableColumns[tableName]
        .map(col => col.column_name || col.column || col.name)
        .filter(Boolean)
    } else {
      columnNames = Object.keys(columnFunctionsTables[tableName] || {})
    }
    
    console.log(`Processing table ${tableName}:`, { 
      tableColumns: tableColumns[tableName], 
      columnNames,
      columnFunctionKeys: Object.keys(columnFunctionsTables[tableName] || {})
    })
    
    if (columnNames.length > 0) {
      tables.push({
        schema_name: 'public',
        table_name: tableName,
        pk: ['id'],
        incremental_col: 'id',
        columns: columnNames.join(',')
      })
    }
  })
  
  console.log('Generated table_sync_config:', { tables })
  return { tables }
}

function buildTableSyncConfig(allPipelineSteps, tableColumns) {
  const ingestionStep = allPipelineSteps?.find(step => step.type === StepTypeEnum.DATA_INGESTION)
  const tableSyncConfig = ingestionStep?.step_config?.table_sync_config

  if (!tableSyncConfig) {
    return { tables: [] }
  }

  if (Array.isArray(tableSyncConfig)) {
    return buildTableSyncConfigFromArray(tableSyncConfig, tableColumns)
  } else if (typeof tableSyncConfig === 'object') {
    return buildTableSyncConfigFromObject(tableSyncConfig, tableColumns)
  }

  return { tables: [] }
}

export function buildStepConfig(formData, allPipelineSteps, tableColumns, selectedTables, configIds) {
  try {
    validateInput(formData)
    
    let stepConfig = createBaseConfig(formData, configIds)
    stepConfig = setConfigType(stepConfig, formData.type)

    switch (formData.type) {
      case StepTypeEnum.DATA_TRANSFORMATION:
        stepConfig = buildTransformationConfig(stepConfig, allPipelineSteps, tableColumns)
        break
      case StepTypeEnum.DATA_VISUALIZATION:
        stepConfig = buildVisualizationConfig(stepConfig)
        break
      case StepTypeEnum.DATA_INGESTION:
        stepConfig = buildIngestionConfig(stepConfig, tableColumns, selectedTables)
        break
      default:
        throw new Error(`Unsupported step type: ${formData.type}`)
    }

    return stepConfig
  } catch (error) {
    console.error('Error building step config:', error)
    throw error
  }
} 