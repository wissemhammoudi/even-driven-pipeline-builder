import React, { useEffect, useState } from 'react'
import DynamicConfigFields from './DynamicConfigFields'
import { getDestinationPluginSection, LoadingState, ErrorState, ConfigHeader } from '../shared/utils'
import { pipelineAPI } from '../../../../../api/pipelineApi'
import toast from 'react-hot-toast'

const DestinationConfigStep = ({
  formData,
  plugins,
  selectedDestinationPlugin,
  pluginConfigSchemas,
  onPluginSelection,
  onConnectionConfigChange,
  setSelectedDestinationPlugin,
  onInputChange
}) => {
  const selectedTool = formData.step_config.tool
  const toolPlugins = plugins?.[selectedTool] || {}
  const pluginSection = getDestinationPluginSection(toolPlugins)
  const [testingConnection, setTestingConnection] = useState(false)

  useEffect(() => {
    if (selectedTool && pluginSection && !selectedDestinationPlugin) {
      const firstPlugin = pluginSection.plugins[0]
      setSelectedDestinationPlugin(firstPlugin.name)
      onPluginSelection(pluginSection.section, firstPlugin.name)
    }
  }, [selectedTool, pluginSection, selectedDestinationPlugin, setSelectedDestinationPlugin, onPluginSelection])

  const testConnection = async () => {
    const currentConfig = formData.step_config.connection_config[pluginSection?.section] || {}
    
    const connectionData = {
      host: currentConfig.host || '',
      dbname: currentConfig.database || currentConfig.dbname || '',
      user: currentConfig.user || currentConfig.username || '',
      password: currentConfig.password || '',
      port: parseInt(currentConfig.port || '5432'),
      schema: currentConfig.schema || 'public'
    }

    if (!connectionData.host || !connectionData.dbname || !connectionData.user || !connectionData.password) {
      toast.error('Please fill in all required connection fields (host, database, username, password)')
      return
    }

    setTestingConnection(true)
    try {
      const result = await pipelineAPI.testConnection(connectionData)
      
      if (result.success) {
        toast.success('Connection successful! Database is accessible.')
      } else {
        toast.error(`Connection failed: ${result.message || 'Unknown error'}`)
      }
    } catch (error) {
      toast.error(`Connection test failed: ${error.message || 'Unknown error'}`)
    } finally {
      setTestingConnection(false)
    }
  }

  if (!selectedTool || !plugins || Object.keys(plugins).length === 0) {
    return <LoadingState color="green" />
  }

  if (!pluginSection) {
    return <ErrorState 
      title="No Destination Configuration Available"
      message="The selected tool doesn't have destination/loader plugins configured."
    />
  }

  return (
    <div className='space-y-6'>
      <ConfigHeader 
        color="green"
        title="Destination Database Configuration"
        message="Configure the connection to your destination database"
      />

      <div>
        <label className='block text-sm font-medium text-gray-700 mb-2'>
          Select Destination Plugin
        </label>
        <select
          value={selectedDestinationPlugin}
          onChange={e => {
            setSelectedDestinationPlugin(e.target.value)
            if (e.target.value) {
              onPluginSelection(pluginSection.section, e.target.value)
            }
          }}
          className='block w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
        >
          <option value=''>Select destination plugin...</option>
          {pluginSection.plugins.map(plugin => (
            <option key={plugin.name} value={plugin.name}>
              {plugin.name}
            </option>
          ))}
        </select>
      </div>

      {selectedDestinationPlugin && (
        <DynamicConfigFields
          pluginType={pluginSection.section}
          pluginSchema={pluginConfigSchemas[pluginSection.section]}
          currentConfig={formData.step_config.connection_config[pluginSection.section] || {}}
          onConfigChange={onConnectionConfigChange}
        />
      )}

      {selectedDestinationPlugin && formData.step_config.tool === 'dlt' && (
        <div>
          <label className='block text-sm font-medium text-gray-700 mb-2'>Target Schema</label>
          <input
            type='text'
            value={formData.step_config.target_schema || ''}
            onChange={e => onInputChange?.('step_config', {
              ...formData.step_config,
              target_schema: e.target.value
            })}
            className='mt-1 block w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-primary focus:border-primary focus:border-gray-300/0 sm:text-sm transition-colors duration-200 placeholder-gray-400'
            placeholder='Enter target schema'
          />
          <p className='mt-1 text-xs text-gray-500'>
            The schema where the data will be loaded in the destination database
          </p>
        </div>
      )}

      {/* Test Connection Button - moved after Target Schema */}
      {selectedDestinationPlugin && (
        <div className='flex justify-center'>
          <button
            type='button'
            onClick={testConnection}
            disabled={testingConnection}
            className={`px-6 py-3 rounded-lg font-medium transition-colors duration-200 ${
              testingConnection
                ? 'bg-gray-400 cursor-not-allowed text-white'
                : 'bg-sky-400 hover:bg-sky-500 text-white'
            }`}
          >
            {testingConnection ? (
              <div className='flex items-center space-x-2'>
                <div className='animate-spin rounded-full h-4 w-4 border-b-2 border-white'></div>
                <span>Testing Connection...</span>
              </div>
            ) : (
              'Test Destination Connection'
            )}
          </button>
        </div>
      )}
    </div>
  )
}

export default DestinationConfigStep
