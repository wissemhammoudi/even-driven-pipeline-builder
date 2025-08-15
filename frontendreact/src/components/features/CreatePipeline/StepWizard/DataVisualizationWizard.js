import React from 'react'
import BasicInfoStep from './BasicInfoStep'
import VisualizationConnectionStep from './DataVisualization/VisualizationConnectionStep'
import ReviewStep from './ReviewStep'

const DataVisualizationWizard = ({
  currentStep,
  formData,
  plugins,
  toolsByType,
  stepTypes,
  existingVisualizationSteps,
  allPipelineSteps,
  selectedSourcePlugin,
  selectedDestinationPlugin,
  utilityType,
  pluginConfigSchemas,
  selectedTables,
  tableColumns,
  searchTerm,
  expandedTables,
  loadingSchema,
  schemaInfo,
  schemaError,
  useDestinationConfig,
  tableSourceOption,
  onInputChange,
  onToolChange,
  onConnectionConfigChange,
  onDestinationConfigChange,
  onPluginSelection,
  setSelectedSourcePlugin,
  setSelectedDestinationPlugin,
  setUtilityType,
  setSelectedTables,
  setTableColumns,
  setSearchTerm,
  setExpandedTables,
  setLoadingSchema,
  setSchemaInfo,
  setSchemaError,
  setUseDestinationConfig,
  setTableSourceOption
}) => {
  const commonProps = {
    formData,
    plugins,
    toolsByType,
    stepTypes,
    existingVisualizationSteps,
    allPipelineSteps,
    selectedSourcePlugin,
    selectedDestinationPlugin,
    utilityType,
    pluginConfigSchemas,
    selectedTables,
    tableColumns,
    searchTerm,
    expandedTables,
    loadingSchema,
    schemaInfo,
    schemaError,
    useDestinationConfig,
    tableSourceOption,
    onInputChange,
    onToolChange,
    onConnectionConfigChange,
    onDestinationConfigChange,
    onPluginSelection,
    setSelectedSourcePlugin,
    setSelectedDestinationPlugin,
    setUtilityType,
    setSelectedTables,
    setTableColumns,
    setSearchTerm,
    setExpandedTables,
    setLoadingSchema,
    setSchemaInfo,
    setSchemaError,
    setUseDestinationConfig,
    setTableSourceOption
  }

  switch (currentStep) {
    case 1:
      return <BasicInfoStep {...commonProps} />
    case 2:
      return <VisualizationConnectionStep {...commonProps} />
    case 3:
      return <ReviewStep {...commonProps} />
    default:
      return null
  }
}

export default DataVisualizationWizard 