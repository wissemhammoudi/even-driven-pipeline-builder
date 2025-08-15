import React, { useEffect } from 'react'
import DynamicConfigFields from './DynamicConfigFields'
import { getSourcePluginSection, LoadingState, ErrorState, ConfigHeader } from '../shared/utils'

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

  useEffect(() => {
    if (selectedTool && pluginSection && !selectedSourcePlugin) {
      const firstPlugin = pluginSection.plugins[0]
      setSelectedSourcePlugin(firstPlugin.name)
      onPluginSelection(pluginSection.section, firstPlugin.name)
    }
  }, [selectedTool, pluginSection, selectedSourcePlugin, setSelectedSourcePlugin, onPluginSelection])

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
        <DynamicConfigFields
          pluginType={pluginSection.section}
          pluginSchema={pluginConfigSchemas[pluginSection.section]}
          currentConfig={formData.step_config.connection_config[pluginSection.section] || {}}
          onConfigChange={onConnectionConfigChange}
        />
      )}
    </div>
  )
}

export default SourceConfigStep
