import React from 'react'
import PropTypes from 'prop-types'
import PageHeader from '../../components/common/PageHeader'
import PipelineDetailsForm from '../../components/features/CreatePipeline/PipelineDetailsForm'
import PipelineStepsSection from '../../components/features/CreatePipeline/PipelineStepsSection'
import ActionButtons from '../../components/features/CreatePipeline/ActionButtons'
import StepWizardModal from '../../components/features/CreatePipeline/StepWizardModal'
import AccessDeniedMessage from '../../components/features/CreatePipeline/AccessDeniedMessage'

const CreatePipelinePageView = ({
  isAdmin,
  formData,
  onInputChange,
  pipelineSteps,
  loadingStepTypes,
  onAddStep,
  onEditStep,
  onDeleteStep,
  getStepStatus,
  showJsonPreview,
  onToggleJsonPreview,
  jsonPreviewContent,
  onCancel,
  onCreatePipeline,
  creatingPipeline,
  showStepModal,
  closeStepModal,
  currentStep,
  saveStep,
  isEditing,
  existingVisualizationSteps,
  stepTypes,
  allPipelineSteps,
  onNavigateToManagement,
  onNavigateToDashboard
}) => {
  if (!isAdmin) {
    return (
      <AccessDeniedMessage
        onNavigateToManagement={onNavigateToManagement}
        onNavigateToDashboard={onNavigateToDashboard}
      />
    )
  }

  return (
    <div className='space-y-6'>
      <PageHeader
        title='Create New Pipeline'
        subtitle='Build your data pipeline step by step'
      />

      <PipelineDetailsForm 
        formData={formData}
        onInputChange={onInputChange}
      />

      <PipelineStepsSection
        pipelineSteps={pipelineSteps}
        loadingStepTypes={loadingStepTypes}
        onAddStep={onAddStep}
        onEditStep={onEditStep}
        onDeleteStep={onDeleteStep}
        getStepStatus={getStepStatus}
        showJsonPreview={showJsonPreview}
        onToggleJsonPreview={onToggleJsonPreview}
        jsonPreviewContent={jsonPreviewContent}
      />

      <ActionButtons
        onCancel={onCancel}
        onCreatePipeline={onCreatePipeline}
        creatingPipeline={creatingPipeline}
        pipelineSteps={pipelineSteps}
        formData={formData}
      />

      <StepWizardModal
        key={`step-modal-${isEditing ? `edit` : 'new'}`}
        isOpen={showStepModal}
        onClose={closeStepModal}
        step={currentStep}
        onSave={saveStep}
        isEditing={isEditing}
        existingVisualizationSteps={existingVisualizationSteps}
        stepTypes={stepTypes}
        allPipelineSteps={allPipelineSteps}
      />
    </div>
  )
}

CreatePipelinePageView.propTypes = {
  isAdmin: PropTypes.bool.isRequired,
  formData: PropTypes.shape({
    name: PropTypes.string,
    description: PropTypes.string
  }),
  onInputChange: PropTypes.func,
  pipelineSteps: PropTypes.arrayOf(
    PropTypes.shape({
      name: PropTypes.string,
      description: PropTypes.string,
      type: PropTypes.string.isRequired,
      step_config: PropTypes.object
    })
  ),
  loadingStepTypes: PropTypes.bool,
  onAddStep: PropTypes.func,
  onEditStep: PropTypes.func,
  onDeleteStep: PropTypes.func,
  getStepStatus: PropTypes.func,
  showJsonPreview: PropTypes.bool,
  onToggleJsonPreview: PropTypes.func,
  jsonPreviewContent: PropTypes.object,
  onCancel: PropTypes.func,
  onCreatePipeline: PropTypes.func,
  creatingPipeline: PropTypes.bool,
  showStepModal: PropTypes.bool,
  closeStepModal: PropTypes.func,
  currentStep: PropTypes.object,
  saveStep: PropTypes.func,
  isEditing: PropTypes.bool,
  existingVisualizationSteps: PropTypes.array,
  stepTypes: PropTypes.arrayOf(PropTypes.string),
  allPipelineSteps: PropTypes.array,
  onNavigateToManagement: PropTypes.func,
  onNavigateToDashboard: PropTypes.func
}

CreatePipelinePageView.defaultProps = {
  formData: { name: '', description: '' },
  pipelineSteps: [],
  loadingStepTypes: false,
  showJsonPreview: false,
  creatingPipeline: false,
  showStepModal: false,
  isEditing: false,
  existingVisualizationSteps: [],
  stepTypes: [],
  allPipelineSteps: []
}

export default CreatePipelinePageView 