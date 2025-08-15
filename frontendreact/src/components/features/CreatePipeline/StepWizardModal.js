import React from 'react'
import { XMarkIcon } from '@heroicons/react/24/outline'
import DataIngestionWizard from './StepWizard/DataIngestionWizard'
import DataTransformationWizard from './StepWizard/DataTransformationWizard'
import DataVisualizationWizard from './StepWizard/DataVisualizationWizard'
import StepIndicator from './StepWizard/StepIndicator'
import StepWizardNavigation from './StepWizard/StepWizardNavigation'
import { useStepWizardFormRefactored } from './StepWizard/hooks/useStepWizardFormRefactored'
import { getStepTitle, getStepDescription } from './StepWizard/utils'
import { StepTypeEnum } from './StepWizard/utils'
const StepWizardModal = ({
  isOpen,
  onClose,
  onSave,
  isEditing = false,
  step = null,
  existingVisualizationSteps = [],
  stepTypes = [],
  allPipelineSteps = []
}) => {
  const form = useStepWizardFormRefactored({
    isOpen,
    step,
    allPipelineSteps,
    stepTypes,
    existingVisualizationSteps,
    onClose,
    onSave
  })

  const {
    currentStep,
    formData,
    plugins,
    toolsByType,
    selectedSourcePlugin,
    setSelectedSourcePlugin,
    selectedDestinationPlugin,
    setSelectedDestinationPlugin,
    utilityType,
    setUtilityType,
    pluginConfigSchemas,
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
    totalSteps,
    handleInputChange: onInputChange,
    handleToolChange: onToolChange,
    handleConnectionConfigChange: onConnectionConfigChange,
    handleDestinationConfigChange: onDestinationConfigChange,
    handlePluginSelection: onPluginSelection,
    validateCurrentStep,
    nextStep,
    prevStep,
    handleSave,
    handleClose
  } = form

  const renderCurrentStep = () => {
    const commonProps = {
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
    }

    switch (formData.type) {
      case StepTypeEnum.DATA_TRANSFORMATION:
        return <DataTransformationWizard {...commonProps} />
      case StepTypeEnum.DATA_VISUALIZATION:
        return <DataVisualizationWizard {...commonProps} />
      default:
        return <DataIngestionWizard {...commonProps} />
    }
  }

  if (!isOpen) return null

  return (
    <div className='fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50'>
      <div className='relative top-10 mx-auto p-5 border w-11/12 md:w-4/5 lg:w-3/4 xl:w-2/3 shadow-lg rounded-md bg-white max-h-[90vh] overflow-y-auto'>
        <div className='flex justify-between items-center mb-6'>
          <div>
            <h3 className='text-lg font-medium text-gray-900'>
              {isEditing ? 'Edit Step' : 'Create New Step'}
            </h3>
            <p className='text-sm text-gray-500 mt-1'>
              {getStepTitle(formData.type, currentStep)} -{' '}
              {getStepDescription(formData.type, currentStep)}
            </p>
          </div>
          <button
            onClick={handleClose}
            className='text-gray-400 hover:text-gray-600'
          >
            <XMarkIcon className='h-6 w-6' />
          </button>
        </div>
        <StepIndicator totalSteps={totalSteps} currentStep={currentStep} />
        <div className='space-y-6'>{renderCurrentStep()}</div>
        <StepWizardNavigation
          currentStep={currentStep}
          totalSteps={totalSteps}
          onPrev={prevStep}
          onNext={nextStep}
          onCancel={handleClose}
          onSave={handleSave}
          isEditing={isEditing}
          canProceed={validateCurrentStep()}
        />
      </div>
    </div>
  )
}

export default StepWizardModal
