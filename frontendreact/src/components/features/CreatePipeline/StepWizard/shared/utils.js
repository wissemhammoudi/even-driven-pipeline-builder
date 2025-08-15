import React from 'react'


export const getSourcePluginSection = (toolPlugins) => {
  if (toolPlugins.extractors?.length > 0) return { section: 'extractor', plugins: toolPlugins.extractors }
  if (toolPlugins.sources?.length > 0) return { section: 'source', plugins: toolPlugins.sources }
  return null
}

export const getDestinationPluginSection = (toolPlugins) => {
  if (toolPlugins.loaders?.length > 0) return { section: 'loader', plugins: toolPlugins.loaders }
  if (toolPlugins.destinations?.length > 0) return { section: 'destination', plugins: toolPlugins.destinations }
  return null
}

export const getSourceConnection = (connectionConfig, selectedTool) => {
  if (selectedTool === 'meltano') return connectionConfig.extractor
  if (selectedTool === 'dlt') return connectionConfig.source
  if (selectedTool === 'sqlmesh') return connectionConfig.utility
  return connectionConfig.extractor || connectionConfig.source || connectionConfig.utility
}

export const getDestinationConnection = (connectionConfig, selectedTool) => {
  if (selectedTool === 'meltano') return connectionConfig.loader
  if (selectedTool === 'dlt') return connectionConfig.destination
  if (selectedTool === 'sqlmesh') return connectionConfig.utility
  return connectionConfig.loader || connectionConfig.destination || connectionConfig.utility
}

export const validateConnection = (sourceConn) => {
  if (!sourceConn) return 'No source connection configuration found'
  if (!sourceConn.host) return 'Host is required in the source connection'
  if (!sourceConn.password) return 'Password is required in the source connection'
  if (!sourceConn.user && !sourceConn.username) return 'User/Username is required in the source connection'
  if (!sourceConn.database && !sourceConn.dbname) return 'Database/Dbname is required in the source connection'
  return null
}

export const getSchemaName = (sourceConn) => {
  return sourceConn.filter_schema || 
         (Array.isArray(sourceConn.filter_schemas) ? sourceConn.filter_schemas[0] : sourceConn.filter_schemas) ||
         sourceConn.schema || 
         sourceConn.default_target_schema || 
         'public'
}

export const findIngestionStep = (allPipelineSteps) => {
  if (!allPipelineSteps || !Array.isArray(allPipelineSteps)) {
    return null
  }
  return allPipelineSteps.find(
    step =>
      step.type === 'data ingestion' ||
      step.step_type === 'data_ingestion' ||
      step.step_type === 'ingestion' ||
      step.step_type === 'source'
  )
}

export const hasIngestionStep = (ingestionStep) => {
  return ingestionStep && ingestionStep.step_config
}

export const LoadingState = ({ color = 'blue', title = 'Loading...', message = 'Loading configuration...' }) => (
  <div className='space-y-6'>
    <div className={`bg-${color}-50 border border-${color}-200 rounded-lg p-4`}>
      <h4 className={`text-sm font-medium text-${color}-900 mb-2`}>{title}</h4>
      <p className={`text-sm text-${color}-700`}>{message}</p>
    </div>
  </div>
)

export const ErrorState = ({ title, message, className = '' }) => (
  <div className={`space-y-6 ${className}`}>
    <div className='bg-red-50 border border-red-200 rounded-lg p-4'>
      <h4 className='text-sm font-medium text-red-900 mb-2'>{title}</h4>
      <p className='text-sm text-red-700'>{message}</p>
    </div>
  </div>
)

export const WarningState = ({ title, message }) => (
  <div className='bg-yellow-50 border border-yellow-200 rounded-lg p-4'>
    <h4 className='text-sm font-medium text-yellow-900 mb-2'>{title}</h4>
    <p className='text-sm text-yellow-700'>{message}</p>
  </div>
)

export const ConfigHeader = ({ color = 'blue', title, message, children }) => (
  <div className={`bg-${color}-50 border border-${color}-200 rounded-lg p-4`}>
    <h4 className={`text-sm font-medium text-${color}-900 mb-2`}>{title}</h4>
    <p className={`text-sm text-${color}-700`}>{message}</p>
    {children}
  </div>
)

export const TabButton = ({ active, onClick, children, className = '' }) => (
  <button
    onClick={onClick}
    className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
      active
        ? 'bg-primary text-white'
        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
    } ${className}`}
  >
    {children}
  </button>
)

export const LoadingSpinner = ({ size = 'h-4 w-4', className = '' }) => (
  <div className={`animate-spin rounded-full border-b-2 border-white ${size} ${className}`}></div>
) 