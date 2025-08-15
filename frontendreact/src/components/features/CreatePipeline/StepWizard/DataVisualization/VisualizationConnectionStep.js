import React, { useEffect } from 'react'
import { ConfigHeader } from '../shared/utils'
import { useDestinationConfig } from '../shared/useDestinationConfig'
import { useUtilityPlugin } from '../shared/useUtilityPlugin'
import ExistingConnectionDisplay from '../shared/ExistingConnectionDisplay'
import DynamicConfigFields from '../DataIngestion/DynamicConfigFields'

const DEFAULT_DESTINATION_CONFIG = {
  host: '',
  port: 5432,
  database: '',
  user: '',
  password: '',
  schema: 'public'
}

const VisualizationConnectionStep = ({
  formData,
  plugins,
  pluginConfigSchemas,
  allPipelineSteps,
  useDestinationConfig: useExistingConnection,
  onPluginSelection,
  onConnectionConfigChange,
  setUseDestinationConfig,
  onInputChange
}) => {
  const { destinationConfig, canUseExistingConnection } = useDestinationConfig(allPipelineSteps)
  const { utilityType } = useUtilityPlugin(plugins, onPluginSelection, 'superset')

  useEffect(() => {
    if (useExistingConnection && destinationConfig && onInputChange) {
      const config = {
        host: destinationConfig.host,
        port: destinationConfig.port,
        database: destinationConfig.database,
        user: destinationConfig.user,
        password: destinationConfig.password,
        schema: destinationConfig.schema
      }

      onInputChange('step_config', {
        ...formData.step_config,
        destination_config: config
      })
    }
  }, [useExistingConnection, destinationConfig, onInputChange, formData.step_config])

  useEffect(() => {
    if (onInputChange && !formData.step_config.destination_config) {
      onInputChange('step_config', {
        ...formData.step_config,
        destination_config: DEFAULT_DESTINATION_CONFIG
      })
    }
  }, [onInputChange, formData.step_config.destination_config])

  useEffect(() => {
    const currentDestConfig = formData.step_config.destination_config || {}
    let needsUpdate = false
    let cleanConfig = { ...currentDestConfig }
    
    if (currentDestConfig.utility) {
      const { utility, ...rest } = cleanConfig
      cleanConfig = rest
      needsUpdate = true
    }
    
    if (cleanConfig.port && typeof cleanConfig.port === 'string') {
      cleanConfig.port = parseInt(cleanConfig.port, 10) || 5432
      needsUpdate = true
    }
    
    if (needsUpdate && onInputChange) {
      onInputChange('step_config', {
        ...formData.step_config,
        destination_config: cleanConfig
      })
    }
  }, [formData.step_config.destination_config, onInputChange])

  const handleUseExistingConnectionChange = (useExisting) => {
    setUseDestinationConfig(useExisting)
    
    if (useExisting && destinationConfig && onInputChange) {
      const config = {
        host: destinationConfig.host,
        port: destinationConfig.port,
        database: destinationConfig.database,
        user: destinationConfig.user,
        password: destinationConfig.password,
        schema: destinationConfig.schema
      }

      onInputChange('step_config', {
        ...formData.step_config,
        destination_config: config
      })
    } else if (!useExisting && onInputChange) {
      onInputChange('step_config', {
        ...formData.step_config,
        destination_config: DEFAULT_DESTINATION_CONFIG
      })
    }
  }

  const handleNewConnectionSelect = () => {
    if (onInputChange) {
      onInputChange('step_config', {
        ...formData.step_config,
        destination_config: DEFAULT_DESTINATION_CONFIG
      })
    }
  }

  const handleConfigChange = (pluginType, field, value) => {
    if (field === 'destination_config') {
      if (onInputChange) {
        onInputChange('step_config', {
          ...formData.step_config,
          destination_config: value
        })
      }
    } else {
      if (onInputChange) {
        let finalValue = value
        if (field === 'port') {
          finalValue = parseInt(value, 10) || 5432
        }
        
        onInputChange('step_config', {
          ...formData.step_config,
          destination_config: {
            ...formData.step_config.destination_config,
            [field]: finalValue
          }
        })
      }
    }
  }

  return (
    <div className='space-y-6'>
      <ConfigHeader 
        title="Database Connection Configuration"
        message="Configure the database connection for visualization data source"
      />

      {canUseExistingConnection && (
        <div className='bg-gray-50 border border-gray-200 rounded-lg p-4'>
          <h5 className='text-sm font-medium text-gray-900 mb-2'>
            Database Connection
          </h5>
          <div className='space-y-3'>
            <label className='flex items-center'>
              <input
                type='radio'
                checked={useExistingConnection}
                onChange={() => handleUseExistingConnectionChange(true)}
                className='h-4 w-4 text-primary focus:ring-primary border-gray-300'
              />
              <span className='ml-2 text-sm text-gray-700'>
                Use existing connection from{' '}
                {destinationConfig?.source === 'transformation'
                  ? 'transformation step'
                  : 'ingestion step'}
              </span>
            </label>
            <label className='flex items-center'>
              <input
                type='radio'
                checked={!useExistingConnection}
                onChange={() => {
                  handleUseExistingConnectionChange(false)
                  handleNewConnectionSelect()
                }}
                className='h-4 w-4 text-primary focus:ring-primary border-gray-300'
              />
              <span className='ml-2 text-sm text-gray-700'>
                Configure new connection
              </span>
            </label>
          </div>
        </div>
      )}

      {canUseExistingConnection && useExistingConnection && (
        <ExistingConnectionDisplay 
          destinationConfig={destinationConfig}
          useExistingConnection={useExistingConnection}
        />
      )}

      {canUseExistingConnection && useExistingConnection ? (
        <div>
          <h5 className='text-sm font-medium text-gray-900 mb-2'>
            Connection Configuration
          </h5>
          <div className='bg-blue-50 border border-blue-200 rounded-lg p-4'>
            <p className='text-sm text-blue-700'>
              Using existing connection configuration from{' '}
              {destinationConfig?.source === 'transformation'
                ? 'the transformation step'
                : 'the ingestion step'}
              .
            </p>
          </div>
        </div>
      ) : (
        <div>
          <h5 className='text-sm font-medium text-gray-900 mb-2'>
            Database Connection
          </h5>
          <div className='bg-gray-50 border border-gray-200 rounded-lg p-4'>
            <p className='text-sm text-gray-700 mb-4'>
              Configure the database connection for your visualization data source. Superset will connect to this database to read data for charts and dashboards.
            </p>

            {utilityType && pluginConfigSchemas.utility ? (
              <DynamicConfigFields
                pluginType='utility'
                pluginSchema={pluginConfigSchemas.utility}
                currentConfig={formData.step_config.destination_config || DEFAULT_DESTINATION_CONFIG}
                onConfigChange={handleConfigChange}
              />
            ) : (
              <div className='text-center py-4 text-gray-500'>
                <p>Loading utility plugin configuration...</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default VisualizationConnectionStep
