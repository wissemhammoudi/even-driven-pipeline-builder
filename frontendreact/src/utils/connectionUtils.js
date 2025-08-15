import { StepTypeEnum } from '../components/features/CreatePipeline/StepWizard/utils'
export const extractSourceConfig = (connectionConfig) => {
  if (!connectionConfig) return {}
  
  if (connectionConfig.source) {
    return connectionConfig.source
  }
  
  if (connectionConfig.extractor) {
    return connectionConfig.extractor
  }
  
  return connectionConfig
}

export const extractDestinationConfig = (connectionConfig) => {
  if (!connectionConfig) return {}
  
  if (connectionConfig.destination) {
    return connectionConfig.destination
  }
  
  if (connectionConfig.loader) {
    return connectionConfig.loader
  }
  
  return connectionConfig
}

export const mergeConnectionConfigs = (sourceConfig, destinationConfig) => {
  const merged = {
    ...sourceConfig,
    ...destinationConfig
  }
  
  return merged
}

export const findTransformationDestinationConfig = (allPipelineSteps) => {
  if (!allPipelineSteps || !Array.isArray(allPipelineSteps)) {
    return null
  }
  
  const transformationStep = allPipelineSteps.find(step => 
    step.type === StepTypeEnum.DATA_TRANSFORMATION || 
    step.step_type === StepTypeEnum.DATA_TRANSFORMATION
  )
  
  if (transformationStep?.step_config?.destination_config) {
    return transformationStep.step_config.destination_config
  }
  
  return null
}

export const buildConnectionString = (config, databaseType = 'postgresql') => {
  if (!config || !config.host || !config.username || !config.password || !config.database) {
    return null
  }
  
  switch (databaseType.toLowerCase()) {
    case 'postgresql':
    case 'postgres':
      return `postgresql://${config.username}:${config.password}@${config.host}:${config.port || 5432}/${config.database}`
    case 'mysql':
      return `mysql://${config.username}:${config.password}@${config.host}:${config.port || 3306}/${config.database}`
    case 'mssql':
    case 'sqlserver':
      return `mssql://${config.username}:${config.password}@${config.host}:${config.port || 1433}/${config.database}`
    default:
      return null
  }
}

export const parseConnectionString = (connectionString) => {
  if (!connectionString) return null
  
  try {
    const url = new URL(connectionString)
    const config = {
      host: url.hostname,
      port: parseInt(url.port) || 5432,
      username: url.username,
      password: url.password,
      database: url.pathname.substring(1),
      databaseType: url.protocol.replace(':', '')
    }
    
    return config
  } catch (error) {
    return null
  }
}

export const validateConnectionConfig = (config) => {
  if (!config) return false
  
  const requiredFields = ['host', 'username', 'password', 'database']
  return requiredFields.every(field => config[field] && config[field].trim() !== '')
} 