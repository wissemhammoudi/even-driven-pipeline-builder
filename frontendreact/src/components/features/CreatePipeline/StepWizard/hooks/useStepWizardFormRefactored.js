import { useState, useEffect, useCallback } from 'react'
import { usePluginManagement } from './usePluginManagement'
import { useFormValidation } from './useFormValidation'
import { buildStepConfig } from '../utils/stepConfigBuilder'
import { StepTypeEnum, ToolEnum } from '../utils'

export function useStepWizardFormRefactored({
  isOpen,
  step,
  allPipelineSteps,
  stepTypes,
  existingVisualizationSteps,
  onClose,
  onSave
}) {
  const [currentStep, setCurrentStep] = useState(1)
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    type: StepTypeEnum.DATA_INGESTION,
    step_config: {
      config_ids: [],
      connection_config: {
        extractor: {},
        loader: {},
        source: {},
        destination: {}
      },
      destination_config: {},
      tool: null
    },
    order: 1
  })

  const [selectedSourcePlugin, setSelectedSourcePlugin] = useState('')
  const [selectedDestinationPlugin, setSelectedDestinationPlugin] = useState('')
  const [utilityType, setUtilityType] = useState('')
  const [selectedTables, setSelectedTables] = useState(new Set())
  const [tableColumns, setTableColumns] = useState({})
  const [searchTerm, setSearchTerm] = useState('')
  const [expandedTables, setExpandedTables] = useState(new Set())
  const [loadingSchema, setLoadingSchema] = useState(false)
  const [schemaInfo, setSchemaInfo] = useState({})
  const [schemaError, setSchemaError] = useState('')
  const [useDestinationConfig, setUseDestinationConfig] = useState(true)
  const [tableSourceOption, setTableSourceOption] = useState('use_ingestion')

  const {
    plugins,
    toolsByType,
    pluginConfigSchemas,
    configIds,
    setConfigIds,
    setPluginConfigSchemas,
    loadPlugins,
    handlePluginSelection: handlePluginSelectionBase
  } = usePluginManagement(formData, handleToolChange)

  const { validateCurrentStep } = useFormValidation()

  const getTotalSteps = () => {
    if (formData.type === StepTypeEnum.DATA_TRANSFORMATION) {
      return 4
    } else if (formData.type === StepTypeEnum.DATA_VISUALIZATION) {
      return 3
    }
    return 5
  }
  const totalSteps = getTotalSteps()

  useEffect(() => {
    if (isOpen) {
      loadPlugins()
      setCurrentStep(1)

      if (!step || Object.keys(step).length === 0) {
        resetForm()
      }
    }
  }, [isOpen, step])

  useEffect(() => {
    if (
      Object.keys(toolsByType).length > 0 &&
      formData.type &&
      !formData.step_config.tool &&
      toolsByType[formData.type] &&
      toolsByType[formData.type].length > 0
    ) {
      const defaultTool = toolsByType[formData.type][0]
      handleToolChange(defaultTool)
    }
  }, [toolsByType, formData.type, formData.step_config.tool])

  useEffect(() => {
    if (isOpen && step && Object.keys(step).length > 0) {
      let tool = step.step_config?.tool
      if (step.type === StepTypeEnum.DATA_VISUALIZATION && !tool) {
        tool = ToolEnum.SUPERSET
      }

      setFormData({
        name: step.name || '',
        description: step.description || '',
        type: step.type || StepTypeEnum.DATA_INGESTION,
        step_config: {
          config_ids: step.step_config?.config_ids || [],
          connection_config: step.step_config?.connection_config || {
            extractor: {},
            loader: {},
            source: {},
            destination: {}
          },
          destination_config: step.step_config?.destination_config || {},
          tool: tool
        },
        order: step.order || 1
      })
      setSelectedTables(
        new Set(Object.keys(step.step_config?.table_sync_map || {}))
      )

      if (tool === ToolEnum.MELTANO) {
        setSelectedSourcePlugin(step.step_config?.extractor_type || '')
        setSelectedDestinationPlugin(step.step_config?.loader_type || '')
      } else if (tool === ToolEnum.DLT) {
        setSelectedSourcePlugin(step.step_config?.source || '')
        setSelectedDestinationPlugin(step.step_config?.destination || '')
      }

      if (
        step.type === StepTypeEnum.DATA_TRANSFORMATION ||
        step.type === StepTypeEnum.DATA_VISUALIZATION
      ) {
        setUtilityType(step.step_config?.utility_type || '')
      }
    }
  }, [step])

  function handleToolChange(tool) {
    setFormData(prev => ({
      ...prev,
      step_config: {
        ...prev.step_config,
        tool: tool,
        config_ids: prev.step_config.config_ids || [],
        connection_config: {
          extractor: {},
          loader: {},
          source: {},
          destination: {}
        },
        destination_config: {},
        ...(tool === ToolEnum.SQLMESH && prev.type === StepTypeEnum.DATA_TRANSFORMATION
          ? { dialect: 'postgres' }
          : {})
      }
    }))
  }

  const resetForm = () => {
    let defaultType = StepTypeEnum.DATA_INGESTION
    let tool = null

    if (allPipelineSteps && allPipelineSteps.length > 0) {
      const lastStep = allPipelineSteps[allPipelineSteps.length - 1]
      if (lastStep.type === StepTypeEnum.DATA_INGESTION) {
        defaultType = StepTypeEnum.DATA_TRANSFORMATION
      } else if (lastStep.type === StepTypeEnum.DATA_TRANSFORMATION) {
        defaultType = StepTypeEnum.DATA_VISUALIZATION
      }

      if (defaultType === StepTypeEnum.DATA_VISUALIZATION) {
        tool = ToolEnum.SUPERSET
      } else {
        const firstStep = allPipelineSteps[0]
        if (firstStep.step_config && firstStep.step_config.tool) {
          const firstTool = firstStep.step_config.tool
          if (firstTool === ToolEnum.MELTANO) {
            tool = firstTool
          } else if (
            firstTool === ToolEnum.DLT &&
            defaultType === StepTypeEnum.DATA_TRANSFORMATION
          ) {
            tool = ToolEnum.SQLMESH
          }
        }
      }
    }

    setFormData({
      name: '',
      description: '',
      type: defaultType,
      step_config: {
        config_ids: [],
        connection_config: {
          extractor: {},
          loader: {},
          source: {},
          destination: {}
        },
        destination_config: {},
        tool: tool
      },
      order: allPipelineSteps ? allPipelineSteps.length + 1 : 1
    })
    setSelectedSourcePlugin('')
    setSelectedDestinationPlugin('')
    setUtilityType('')
    setSelectedTables(new Set())
    setPluginConfigSchemas({})
    setSchemaInfo({})
    setSchemaError('')
    setConfigIds([])
  }

  const handleInputChange = useCallback((field, value) => {
    setFormData(prev => {
      const newData = { ...prev }

      if (field === 'name' || field === 'description' || field === 'type') {
        newData[field] = value
      } else if (field === 'step_config') {
        const currentStepConfig = newData.step_config || {}
        const newStepConfig = { ...currentStepConfig, ...value }
        
        if (JSON.stringify(currentStepConfig) !== JSON.stringify(newStepConfig)) {
          newData.step_config = newStepConfig
        } else {
          return prev
        }
      }

      if (field === 'type') {
        let defaultTool = null
        if (value === StepTypeEnum.DATA_VISUALIZATION) {
          defaultTool = ToolEnum.SUPERSET
        } else if (value === StepTypeEnum.DATA_TRANSFORMATION) {
          if (allPipelineSteps && allPipelineSteps.length > 0) {
            const firstStep = allPipelineSteps[0]
            if (firstStep.step_config && firstStep.step_config.tool === ToolEnum.DLT) {
              defaultTool = ToolEnum.SQLMESH
            } else {
              defaultTool = ToolEnum.DBT
            }
          } else {
            defaultTool = ToolEnum.DBT
          }
        } else if (value === StepTypeEnum.DATA_INGESTION) {
          if (toolsByType[value] && toolsByType[value].length > 0) {
            defaultTool = toolsByType[value][0]
          }
        }

        newData.step_config = {
          ...newData.step_config,
          tool: defaultTool,
          connection_config: {
            extractor: {},
            loader: {},
            source: {},
            destination: {}
          },
          config_ids: newData.step_config.config_ids || []
        }
      }

      return newData
    })
  }, [allPipelineSteps, toolsByType])

  const handleConnectionConfigChange = (section, key, value) => {
    setFormData(prev => ({
      ...prev,
      step_config: {
        ...prev.step_config,
        connection_config: {
          ...prev.step_config.connection_config,
          [section]: {
            ...prev.step_config.connection_config[section],
            [key]: value
          }
        }
      }
    }))
  }

  const handleDestinationConfigChange = (key, value) => {
    setFormData(prev => {
      const updatedData = {
        ...prev,
        step_config: {
          ...prev.step_config,
          destination_config: {
            ...prev.step_config.destination_config,
            [key]: value
          }
        }
      }
      return updatedData
    })
  }

  const handlePluginSelection = async (pluginType, pluginName) => {
    await handlePluginSelectionBase(pluginType, pluginName, formData, setFormData)
  }

  const nextStep = () => {
    if (validateCurrentStep(currentStep, formData, selectedSourcePlugin, selectedDestinationPlugin, selectedTables) && currentStep < totalSteps) {
      setCurrentStep(currentStep + 1)
    }
  }

  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1)
    }
  }

  const handleSave = async () => {
    const stepConfig = buildStepConfig(formData, allPipelineSteps, tableColumns, selectedTables, configIds)

    let finalFormData = {
      ...formData,
      step_config: stepConfig
    }

    if (onSave) {
      onSave(finalFormData)
    }
  }

  const handleClose = () => {
    resetForm()
    if (onClose) {
      onClose()
    }
  }

  return {
    currentStep,
    setCurrentStep,
    formData,
    setFormData,
    plugins,
    toolsByType,
    selectedSourcePlugin,
    setSelectedSourcePlugin,
    selectedDestinationPlugin,
    setSelectedDestinationPlugin,
    utilityType,
    setUtilityType,
    configIds,
    setConfigIds,
    pluginConfigSchemas,
    setPluginConfigSchemas,
    selectedTables,
    setSelectedTables,
    tableColumns,
    setTableColumns,
    searchTerm,
    setSearchTerm,
    expandedTables,
    setExpandedTables,
    loadingSchema,
    setLoadingSchema,
    schemaInfo,
    setSchemaInfo,
    schemaError,
    setSchemaError,
    useDestinationConfig,
    setUseDestinationConfig,
    tableSourceOption,
    setTableSourceOption,
    getTotalSteps,
    totalSteps,
    loadPlugins,
    resetForm,
    handleInputChange,
    handleToolChange,
    handleConnectionConfigChange,
    handleDestinationConfigChange,
    handlePluginSelection,
    validateCurrentStep: () => validateCurrentStep(currentStep, formData, selectedSourcePlugin, selectedDestinationPlugin, selectedTables),
    nextStep,
    prevStep,
    handleSave,
    handleClose
  }
} 