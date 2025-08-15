import React, { useEffect } from 'react'
import { ConfigHeader, WarningState } from '../shared/utils'
import { useDestinationConfig } from '../shared/useDestinationConfig'
import { useUtilityPlugin } from '../shared/useUtilityPlugin'
import ExistingConnectionDisplay from '../shared/ExistingConnectionDisplay'
import DynamicConfigFields from '../DataIngestion/DynamicConfigFields'

const TransformationConnectionStep = ({
  formData,
  plugins,
  pluginConfigSchemas,
  allPipelineSteps,
  useDestinationConfig: useExistingConnection,
  onPluginSelection,
  onConnectionConfigChange,
  onDestinationConfigChange,
  onDestinationConfigUpdate,
  setUseDestinationConfig,
  onToolChange,
  onInputChange
}) => {
  const selectedTool = formData.step_config.tool
  const { destinationConfig, canUseExistingConnection } = useDestinationConfig(allPipelineSteps)
  const { utilityType, utilityPlugins, setUtilityType } = useUtilityPlugin(plugins, onPluginSelection, selectedTool)

  useEffect(() => {
    if (
      !selectedTool &&
      allPipelineSteps &&
      allPipelineSteps.length > 0
    ) {
      const firstStep = allPipelineSteps[0]
      if (firstStep?.step_config?.tool) {
        const firstTool = firstStep.step_config.tool
        if (firstTool === 'meltano') {
          onToolChange('meltano')
        } else if (firstTool === 'dlt') {
          onToolChange('sqlmesh')
        }
      } else {
        onToolChange('meltano')
      }
    } else if (!selectedTool) {
      onToolChange('meltano')
    }
  }, [allPipelineSteps, onToolChange, selectedTool])

  useEffect(() => {
    if (useExistingConnection && destinationConfig && onDestinationConfigChange) {
      onDestinationConfigChange('host', destinationConfig.host || '')
      onDestinationConfigChange('port', destinationConfig.port || '')
      onDestinationConfigChange('database', destinationConfig.database || '')
      onDestinationConfigChange('user', destinationConfig.user || '')
      onDestinationConfigChange('password', destinationConfig.password || '')
      onDestinationConfigChange('schema', destinationConfig.schema || '')
    }
  }, [useExistingConnection, destinationConfig, onDestinationConfigChange])

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
    
    if (useExisting && destinationConfig && onDestinationConfigChange) {
      onDestinationConfigChange('host', destinationConfig.host || '')
      onDestinationConfigChange('port', destinationConfig.port || '')
      onDestinationConfigChange('database', destinationConfig.database || '')
      onDestinationConfigChange('user', destinationConfig.user || '')
      onDestinationConfigChange('password', destinationConfig.password || '')
      onDestinationConfigChange('schema', destinationConfig.schema || '')
    }
  }

  const handleNewConnectionSelect = () => {
    if (onDestinationConfigChange) {
      onDestinationConfigChange('host', '')
      onDestinationConfigChange('port', '')
      onDestinationConfigChange('database', '')
      onDestinationConfigChange('user', '')
      onDestinationConfigChange('password', '')
      onDestinationConfigChange('schema', '')
    }
  }

  const handleConfigChange = (pluginType, field, value) => {
    if (field === 'destination_config') {
      if (onDestinationConfigUpdate) {
        onDestinationConfigUpdate(value)
      }
    } else {
      if (onDestinationConfigChange) {
        let finalValue = value
        if (field === 'port') {
          finalValue = parseInt(value, 10) || 5432
        }
        onDestinationConfigChange(field, finalValue)
      }
    }
  }

  if (!selectedTool) {
    return (
      <WarningState 
        title="Determining Tool"
        message="Please wait while we determine the appropriate transformation tool..."
      />
    )
  }

  return (
    <div className='space-y-6'>
      <ConfigHeader 
        title="Transformation Utility Selection"
        message={`Using ${selectedTool.charAt(0).toUpperCase() + selectedTool.slice(1)} for transformation. Select the utility plugin for your transformation needs.`}
      />

      <div>
        <label className='block text-sm font-medium text-gray-700 mb-2'>
          Select Utility Plugin
        </label>
        <select
          value={utilityType}
          onChange={e => setUtilityType(e.target.value)}
          className='block w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
        >
          <option value=''>Select utility plugin...</option>
          {utilityPlugins.map(plugin => (
            <option key={plugin.name} value={plugin.name}>
              {plugin.name}
            </option>
          ))}
        </select>
      </div>

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
              Using existing connection configuration from the ingestion step.
            </p>
          </div>
        </div>
      ) : (
        <div>
          <h5 className='text-sm font-medium text-gray-900 mb-2'>
            {canUseExistingConnection ? 'New Database Connection' : 'Database Connection'}
          </h5>
          <div className='bg-gray-50 border border-gray-200 rounded-lg p-4'>
            <p className='text-sm text-gray-700 mb-4'>
              {canUseExistingConnection
                ? `Configure a new database connection for your ${selectedTool} transformation step.`
                : `Configure the database connection for your ${selectedTool} transformation step. ${selectedTool.charAt(0).toUpperCase() + selectedTool.slice(1)} will connect to and write to this database.`
              }
            </p>

            {utilityType && pluginConfigSchemas.utility ? (
              <DynamicConfigFields
                pluginType='utility'
                pluginSchema={pluginConfigSchemas.utility}
                currentConfig={formData.step_config.destination_config || {}}
                onConfigChange={handleConfigChange}
              />
            ) : (
              <WarningState 
                title="Configuration Loading"
                message={
                  utilityType
                    ? 'Loading utility plugin configuration...'
                    : 'Please wait while the utility plugin is being configured...'
                }
              />
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default TransformationConnectionStep
