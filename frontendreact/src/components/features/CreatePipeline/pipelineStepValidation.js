import { StepTypeEnum } from './StepWizard/utils'

function hasValidConnection(connSection) {
  if (!connSection || typeof connSection !== 'object') {
    return false
  }

  const hasHost = Boolean(connSection.host)
  const hasPassword = Boolean(connSection.password)
  const hasUser = Boolean(connSection.user || connSection.username)
  const hasDatabase = Boolean(connSection.database || connSection.dbname)

  return hasHost && hasPassword && hasUser && hasDatabase
}

function validateTransformationDestination(destinationConfig) {
  if (!destinationConfig || typeof destinationConfig !== 'object') {
    return false
  }

  const hasHost = Boolean(destinationConfig.host)
  const hasDatabase = Boolean(destinationConfig.database || destinationConfig.dbname)
  const hasUser = Boolean(destinationConfig.user || destinationConfig.username)
  const hasPassword = Boolean(destinationConfig.password)

  return hasHost && hasDatabase && hasUser && hasPassword
}

function validateMeltanoTransformation(config) {
  if (!config.utility_type) {
    return false
  }

  return validateTransformationDestination(config.destination_config)
}

function validateTransformationStep(config) {
  if (!config.utility_type) {
    return false
  }

  if (config.tool === 'meltano') {
    return validateMeltanoTransformation(config)
  }

  return hasValidConnection(config.destination_config)
}

function validateVisualizationStep(config) {
  const destinationConfig = config.destination_config
  
  if (!destinationConfig || typeof destinationConfig !== 'object') {
    return false
  }

  if (destinationConfig.sqlalchemy_uri) {
    return true
  }

  return hasValidConnection(destinationConfig)
}

function validateMeltanoIngestion(connectionConfig) {
  const extractorConfig = connectionConfig.extractor || {}
  const loaderConfig = connectionConfig.loader || {}

  return hasValidConnection(extractorConfig) && hasValidConnection(loaderConfig)
}

function validateDltIngestion(connectionConfig) {
  const sourceConfig = connectionConfig.source || {}
  const destinationConfig = connectionConfig.destination || {}

  return hasValidConnection(sourceConfig) && hasValidConnection(destinationConfig)
}

function validateIngestionStep(config) {
  const connectionConfig = config.connection_config
  
  if (!connectionConfig || typeof connectionConfig !== 'object') {
    return false
  }

  if (config.tool === 'meltano') {
    return validateMeltanoIngestion(connectionConfig)
  }

  if (config.tool === 'dlt') {
    return validateDltIngestion(connectionConfig)
  }
  return Object.values(connectionConfig).some(hasValidConnection)
}

export function isStepConfigured(step) {
  if (!step || typeof step !== 'object') {
    return false
  }

  const config = step.step_config
  if (!config || typeof config !== 'object') {
    return false
  }

  if (!config.tool) {
    return false
  }

  switch (step.type) {
    case StepTypeEnum.DATA_TRANSFORMATION:
      return validateTransformationStep(config)
    
    case StepTypeEnum.DATA_VISUALIZATION:
      return validateVisualizationStep(config)
    
    default:
      return validateIngestionStep(config)
  }
} 