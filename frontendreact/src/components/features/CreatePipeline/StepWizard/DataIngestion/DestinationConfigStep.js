import React, { useEffect } from 'react'
import DynamicConfigFields from './DynamicConfigFields'
import { getDestinationPluginSection, LoadingState, ErrorState, ConfigHeader } from '../shared/utils'

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

  useEffect(() => {
    if (selectedTool && pluginSection && !selectedDestinationPlugin) {
      const firstPlugin = pluginSection.plugins[0]
      setSelectedDestinationPlugin(firstPlugin.name)
      onPluginSelection(pluginSection.section, firstPlugin.name)
    }
  }, [selectedTool, pluginSection, selectedDestinationPlugin, setSelectedDestinationPlugin, onPluginSelection])

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
    </div>
  )
}

export default DestinationConfigStep
