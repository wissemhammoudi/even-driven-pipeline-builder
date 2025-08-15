import React, { useState, useEffect, useMemo, useCallback } from 'react'
import toast from 'react-hot-toast'
import stepConfigurationApi from '../../api/stepConfigurationApi'
import { processTransformationsFromConfig } from '../../components/features/ConfigManagementPage/utils'
import ConfigManagementView from '../../components/features/ConfigManagementPage/ConfigManagementView'

const StepConfigManagementPage = () => {
  const [state, setState] = useState({
    allTools: [],
    selectedTool: null,
    selectedType: null,
    toolConfigs: [],
    stepTypes: [],
    loading: false,
    showConfigModal: false,
    selectedConfig: null,
    currentPage: 1,
    showDeprecated: false,
    showTransformations: false
  })

  const pageSize = 5

  useEffect(() => {
    loadTools()
  }, [])

  useEffect(() => {
    if (state.selectedTool) {
      loadToolConfigs()
      loadStepTypes()
    }
  }, [state.selectedTool])

  const loadTools = async () => {
    setState(prev => ({ ...prev, loading: true }))
    try {
      const tools = await stepConfigurationApi.getTools()
      setState(prev => ({ ...prev, allTools: tools, loading: false }))
    } catch (error) {
      toast.error('Failed to load tools')
      setState(prev => ({ ...prev, loading: false }))
    }
  }

  const loadToolConfigs = async () => {
    if (!state.selectedTool) return

    setState(prev => ({ ...prev, loading: true }))
    try {
      const configs = await stepConfigurationApi.getConfigsPerTool(
        state.selectedTool
      )
      setState(prev => ({ ...prev, toolConfigs: configs, loading: false }))
    } catch (error) {
      toast.error('Failed to load tool configurations')
      setState(prev => ({ ...prev, loading: false }))
    }
  }

  const loadStepTypes = async () => {
    try {
      const types = await stepConfigurationApi.getStepTypes()
      setState(prev => ({ ...prev, stepTypes: types }))
    } catch (error) {}
  }

  const handleToolSelect = useCallback(tool => {
    setState(prev => ({
      ...prev,
      selectedTool: tool,
      selectedType: null,
      currentPage: 1
    }))
  }, [])

  const handleTypeSelect = useCallback(type => {
    setState(prev => ({
      ...prev,
      selectedType: type,
      currentPage: 1
    }))
  }, [])

  const handleDeprecateConfig = useCallback(async configId => {
    try {
      const success = await stepConfigurationApi.deprecateStepConfig(configId)
      if (success) {
        toast.success('Configuration deprecated successfully')
        loadToolConfigs()
      } else {
        toast.error('Failed to deprecate configuration')
      }
    } catch (error) {
      toast.error('Failed to deprecate configuration')
    }
  }, [loadToolConfigs])

  const handleViewConfig = useCallback(config => {
    setState(prev => ({
      ...prev,
      selectedConfig: config,
      showConfigModal: true
    }))
  }, [])

  const closeConfigModal = useCallback(() => {
    setState(prev => ({
      ...prev,
      showConfigModal: false,
      selectedConfig: null
    }))
  }, [])

  const handleToggleTransformations = useCallback(() => {
    setState(prev => ({
      ...prev,
      showTransformations: !prev.showTransformations
    }))
  }, [])

  const handleToggleDeprecated = useCallback(() => {
    setState(prev => ({
      ...prev,
      showDeprecated: !prev.showDeprecated
    }))
  }, [])

  const handlePageChange = useCallback(page => {
    setState(prev => ({ ...prev, currentPage: page }))
  }, [])

  const filteredConfigs = useMemo(() => {
    if (!state.selectedTool || !state.selectedType) return []
    return state.toolConfigs.filter(
      config => config.type === state.selectedType
    )
  }, [state.selectedTool, state.selectedType, state.toolConfigs])

  const activeConfigs = useMemo(
    () => filteredConfigs.filter(config => !config.is_deprecated),
    [filteredConfigs]
  )

  const deprecatedConfigs = useMemo(
    () => filteredConfigs.filter(config => config.is_deprecated),
    [filteredConfigs]
  )

  const toolStepTypes = useMemo(() => {
    if (!state.selectedTool || state.toolConfigs.length === 0) return []
    const toolStepTypes = [
      ...new Set(state.toolConfigs.map(config => config.type))
    ]
    return state.stepTypes.filter(type => toolStepTypes.includes(type))
  }, [state.selectedTool, state.toolConfigs, state.stepTypes])

  const transformations = useMemo(
    () =>
      processTransformationsFromConfig(state.selectedTool, state.toolConfigs),
    [state.selectedTool, state.toolConfigs]
  )

  return (
    <ConfigManagementView
      state={state}
      toolStepTypes={toolStepTypes}
      transformations={transformations}
      pageSize={pageSize}
      activeConfigs={activeConfigs}
      deprecatedConfigs={deprecatedConfigs}
      handleToolSelect={handleToolSelect}
      handleTypeSelect={handleTypeSelect}
      handleToggleTransformations={handleToggleTransformations}
      handleToggleDeprecated={handleToggleDeprecated}
      handlePageChange={handlePageChange}
      handleViewConfig={handleViewConfig}
      handleDeprecateConfig={handleDeprecateConfig}
      closeConfigModal={closeConfigModal}
    />
  )
}

export default StepConfigManagementPage