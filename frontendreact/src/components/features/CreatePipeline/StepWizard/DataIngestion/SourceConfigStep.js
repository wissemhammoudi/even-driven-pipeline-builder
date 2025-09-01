import React, { useEffect, useState } from 'react'
import DynamicConfigFields from './DynamicConfigFields'
import { getSourcePluginSection, LoadingState, ErrorState, ConfigHeader } from '../shared/utils'
import { pipelineAPI } from '../../../../../api/pipelineApi'
import toast from 'react-hot-toast'

const SourceConfigStep = ({
  formData,
  plugins,
  selectedSourcePlugin,
  pluginConfigSchemas,
  onPluginSelection,
  onConnectionConfigChange,
  setSelectedSourcePlugin
}) => {
  const selectedTool = formData.step_config.tool
  const toolPlugins = plugins?.[selectedTool] || {}
  const pluginSection = getSourcePluginSection(toolPlugins)
  const [testingConnection, setTestingConnection] = useState(false)

  useEffect(() => {
    if (selectedTool && pluginSection && !selectedSourcePlugin) {
      const firstPlugin = pluginSection.plugins[0]
      setSelectedSourcePlugin(firstPlugin.name)
      onPluginSelection(pluginSection.section, firstPlugin.name)
    }
  }, [selectedTool, pluginSection, selectedSourcePlugin, setSelectedSourcePlugin, onPluginSelection])

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
    return <LoadingState />
  }

  if (!pluginSection) {
    return <ErrorState 
      title="No Source Configuration Available"
      message="The selected tool doesn't have source/extractor plugins configured."
    />
  }

  return (
    <div className='space-y-6'>
      <ConfigHeader 
        title="Source Database Configuration"
        message="Configure the connection to your source database"
      />

      <div>
        <label className='block text-sm font-medium text-gray-700 mb-2'>
          Select Source Plugin
        </label>
        <select
          value={selectedSourcePlugin}
          onChange={e => {
            setSelectedSourcePlugin(e.target.value)
            if (e.target.value) {
              onPluginSelection(pluginSection.section, e.target.value)
            }
          }}
          className='block w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
        >
          <option value=''>Select source plugin...</option>
          {pluginSection.plugins.map(plugin => (
            <option key={plugin.name} value={plugin.name}>
              {plugin.name}
            </option>
          ))}
        </select>
      </div>

      {selectedSourcePlugin && (
        <>
          <DynamicConfigFields
            pluginType={pluginSection.section}
            pluginSchema={pluginConfigSchemas[pluginSection.section]}
            currentConfig={formData.step_config.connection_config[pluginSection.section] || {}}
            onConfigChange={onConnectionConfigChange}
          />
          
          {/* Test Connection Button */}
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
                'Test Source Connection'
              )}
            </button>
          </div>
        </>
      )}
    </div>
  )
}

export default SourceConfigStep
