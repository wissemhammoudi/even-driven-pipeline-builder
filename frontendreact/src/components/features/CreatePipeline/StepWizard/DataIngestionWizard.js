import React from 'react'
import BasicInfoStep from './BasicInfoStep'
import SourceConfigStep from './DataIngestion/SourceConfigStep'
import DestinationConfigStep from './DataIngestion/DestinationConfigStep'
import TableSelectionStep from './DataIngestion/TableSelectionStep'
import ReviewStep from './ReviewStep'

const DataIngestionWizard = ({
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
      return <SourceConfigStep {...commonProps} />
    case 3:
      return <DestinationConfigStep {...commonProps} />
    case 4:
      return (
        <TableSelectionStep
          {...commonProps}
          selectedSourcePlugin={selectedSourcePlugin}
        />
      )
    case 5:
      return <ReviewStep {...commonProps} />
    default:
      return null
  }
}

export default DataIngestionWizard 