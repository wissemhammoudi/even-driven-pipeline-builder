import { useState, useEffect } from 'react'
import { stepConfigurationApi } from '../../../../../api/stepConfigurationApi'
  import { StepTypeEnum, ToolEnum } from '../utils'

export function usePluginManagement(formData, onToolChange) {
  const [plugins, setPlugins] = useState({})
  const [toolsByType, setToolsByType] = useState({})
  const [pluginConfigSchemas, setPluginConfigSchemas] = useState({})
  const [configIds, setConfigIds] = useState([])

  const loadPlugins = async () => {
    try {
      const response = await stepConfigurationApi.getStepConfigs();

      const pluginArray = Array.isArray(response) ? response : response.data;
      const pluginsData = {};
      if (Array.isArray(pluginArray)) {
        pluginArray.forEach(config => {
          const tool = config.tool.toLowerCase();
          if (!pluginsData[tool]) {
            pluginsData[tool] = {
              extractors: [],
              loaders: [],
              utilities: [],
              sources: [],
              destinations: []
            };
          }
          const plugin = {
            name: config.plugin_name,
            label: config.plugin_name,
            type: config.plugin_type,
            config: config.config,
            step_config_id: config.step_config_id
          };
          if (config.plugin_type === 'extractor') {
            pluginsData[tool].extractors.push(plugin);
          } else if (config.plugin_type === 'loader') {
            pluginsData[tool].loaders.push(plugin);
          } else if (config.plugin_type === 'utility') {
            pluginsData[tool].utilities.push(plugin);
          } else if (config.plugin_type === 'source') {
            pluginsData[tool].sources.push(plugin);
          } else if (config.plugin_type === 'destination') {
            pluginsData[tool].destinations.push(plugin);
          }
        });
      } else {
        console.error('Expected array for plugins, got:', pluginArray);
      }
      setPlugins(pluginsData);
      
      const toolsByTypeData = {}
      const stepTypesArr = [
        StepTypeEnum.DATA_INGESTION,
        StepTypeEnum.DATA_TRANSFORMATION,
        StepTypeEnum.DATA_VISUALIZATION
      ]

      for (const stepType of stepTypesArr) {
        try {
          const tools = await stepConfigurationApi.getToolsByType(stepType)
          toolsByTypeData[stepType] = tools
        } catch (error) {
          toolsByTypeData[stepType] = []
        }
      }

      setToolsByType(toolsByTypeData)

      if (
        formData.type &&
        toolsByTypeData[formData.type] &&
        toolsByTypeData[formData.type].length > 0 &&
        !formData.step_config.tool
      ) {
        const firstTool = toolsByTypeData[formData.type][0]
        onToolChange(firstTool)
      }
    } catch (error) {
      console.error('Error loading plugins:', error)
      const fallbackTools = {
        [StepTypeEnum.DATA_INGESTION]: [ToolEnum.DLT, ToolEnum.MELTANO],
        [StepTypeEnum.DATA_TRANSFORMATION]: [ToolEnum.DBT, ToolEnum.SQLMESH],
        [StepTypeEnum.DATA_VISUALIZATION]: [ToolEnum.SUPERSET]
      }
      setToolsByType(fallbackTools)
      
      if (formData.type && !formData.step_config.tool) {
        const defaultTool = fallbackTools[formData.type]?.[0]
        if (defaultTool) {
          onToolChange(defaultTool)
        }
      }
    }
  }

  const handlePluginSelection = async (pluginType, pluginName, formData, setFormData) => {
    let actualPluginType = pluginType
    let stepType = formData.type

    if (formData.type === StepTypeEnum.DATA_INGESTION) {
      const tool = formData.step_config.tool

      if (tool === ToolEnum.MELTANO) {
        if (pluginType === 'source') {
          actualPluginType = 'extractor'
        } else if (pluginType === 'destination') {
          actualPluginType = 'loader'
        }
      } else if (tool === ToolEnum.DLT) {
        if (pluginType === 'extractor') {
          actualPluginType = 'source'
        } else if (pluginType === 'loader') {
          actualPluginType = 'destination'
        }
      }
    }

    if (formData.type === StepTypeEnum.DATA_TRANSFORMATION) {
      actualPluginType = 'utility'
      stepType = StepTypeEnum.DATA_TRANSFORMATION
    }

    if (formData.type === StepTypeEnum.DATA_VISUALIZATION) {
      actualPluginType = 'utility'
      stepType = StepTypeEnum.DATA_VISUALIZATION
    }

    try {
      const tool = formData.step_config.tool

      const response = await stepConfigurationApi.getConfigPerTool(tool, stepType, actualPluginType);

      let pluginConfig;
      if (Array.isArray(response)) {
        pluginConfig = response.find(
          config =>
            config.plugin_name === pluginName &&
            config.plugin_type === actualPluginType &&
            config.type === stepType
        );
      } else if (response && Array.isArray(response.data)) {
        pluginConfig = response.data.find(
          config =>
            config.plugin_name === pluginName &&
            config.plugin_type === actualPluginType &&
            config.type === stepType
        );
      } else {
        pluginConfig = undefined;
      }

      if (pluginConfig) {
        const configId = pluginConfig.step_config_id

        setConfigIds(prev => {

          if (formData.type === StepTypeEnum.DATA_INGESTION) {
            if (!prev.includes(configId)) {
              return [...prev, configId]
            }
            return prev
          } else {
            const newIds = prev.filter(id => id !== configId)
            return [...newIds, configId]
          }
        })

        setPluginConfigSchemas(prev => ({
          ...prev,
          [pluginType]: pluginConfig.config || {},
          [actualPluginType]: pluginConfig.config || {}
        }))

        setFormData(prev => {
          const updatedStepConfig = {
            ...prev.step_config,
            config_ids: [
              ...prev.step_config.config_ids.filter(id => id !== configId),
              configId
            ]
          }

          const tool = prev.step_config.tool
          if (tool === ToolEnum.MELTANO) {
            if (pluginType === 'extractor') {
              updatedStepConfig.extractor_type = pluginName
            } else if (pluginType === 'loader') {
              updatedStepConfig.loader_type = pluginName
            }
          } else if (tool === ToolEnum.DLT) {
            if (pluginType === 'extractor' || pluginType === 'source') {
              updatedStepConfig.source = pluginName
            } else if (
              pluginType === 'loader' ||
              pluginType === 'destination'
            ) {
              updatedStepConfig.destination = pluginName
            }
          }

          if (
            prev.type === StepTypeEnum.DATA_TRANSFORMATION &&
            pluginType === 'utility'
          ) {
            updatedStepConfig.utility_type = pluginName
            if (pluginName.includes('postgres')) {
              updatedStepConfig.dialect = 'postgres'
            } else {
              updatedStepConfig.dialect = 'postgres'
            }
          }

          if (
            prev.type === StepTypeEnum.DATA_VISUALIZATION &&
            pluginType === 'utility'
          ) {
            updatedStepConfig.utility_type = pluginName
          }

          return {
            ...prev,
            step_config: updatedStepConfig
          }
        })
      } else {
        console.warn('Plugin config not found for:', {
          pluginName,
          actualPluginType,
          stepType,
          tool: formData.step_config.tool
        })
      }
    } catch (error) {
      console.error('Error fetching plugin configuration:', error)
    }
  }

  return {
    plugins,
    toolsByType,
    pluginConfigSchemas,
    configIds,
    setConfigIds,
    setPluginConfigSchemas,
    loadPlugins,
    handlePluginSelection
  }
} 