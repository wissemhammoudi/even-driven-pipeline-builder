import React from 'react'
import BasicInfoStep from './BasicInfoStep'
import TransformationConnectionStep from './DataTrasnformation/TransformationConnectionStep'
import TransformationConfigStep from './DataTrasnformation/TransformationConfigStep'
import ReviewStep from './ReviewStep'

const DataTransformationWizard = ({
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
      return <TransformationConnectionStep {...commonProps} />
    case 3:
      return (
        <TransformationConfigStep
          formData={formData}
          utilityType={utilityType}
          allPipelineSteps={allPipelineSteps}
          plugins={plugins}
          pluginConfigSchemas={pluginConfigSchemas}
          onInputChange={onInputChange}
        />
      )
    case 4:
      return <ReviewStep {...commonProps} />
    default:
      return null
  }
}

export default DataTransformationWizard 