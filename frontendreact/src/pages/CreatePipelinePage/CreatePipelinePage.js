import React, { useReducer, useEffect } from 'react'
import PropTypes from 'prop-types'
import { useNavigate } from 'react-router-dom'
import useAuthStore from '../../store/authStore'
import usePipelineStore from '../../store/pipelineStore'
import StepWizardModal from '../../components/features/CreatePipeline/StepWizardModal'
import { stepConfigurationApi } from '../../api/stepConfigurationApi'
import toast from 'react-hot-toast'
import { isStepConfigured } from '../../components/features/CreatePipeline/pipelineStepValidation'
import CreatePipelinePageView from './CreatePipelinePageView'

const initialState = {
  formData: {
    name: '',
    description: ''
  },
  showStepModal: false,
  editingStepIndex: null,
  currentStep: null,
  creatingPipeline: false,
  stepTypes: [],
  loadingStepTypes: true,
  showJsonPreview: false
}

const reducer = (state, action) => {
  switch (action.type) {
    case 'SET_FORM_DATA':
      return {
        ...state,
        formData: {
          ...state.formData,
          [action.field]: action.value
        }
      }
    case 'SET_SHOW_STEP_MODAL':
      return {
        ...state,
        showStepModal: action.payload
      }
    case 'SET_EDITING_STEP_INDEX':
      return {
        ...state,
        editingStepIndex: action.payload
      }
    case 'SET_CURRENT_STEP':
      return {
        ...state,
        currentStep: action.payload
      }
    case 'SET_CREATING_PIPELINE':
      return {
        ...state,
        creatingPipeline: action.payload
      }
    case 'SET_STEP_TYPES':
      return {
        ...state,
        stepTypes: action.payload
      }
    case 'SET_LOADING_STEP_TYPES':
      return {
        ...state,
        loadingStepTypes: action.payload
      }
    case 'SET_SHOW_JSON_PREVIEW':
      return {
        ...state,
        showJsonPreview: action.payload
      }
    case 'RESET_MODAL_STATE':
      return {
        ...state,
        showStepModal: false,
        editingStepIndex: null,
        currentStep: null
      }
    default:
      return state
  }
}

const CreatePipelinePage = () => {
  const navigate = useNavigate()
  const { user, isAdmin } = useAuthStore()
  const {
    pipelineSteps,
    addPipelineStep,
    updatePipelineStep,
    removePipelineStep,
    clearPipelineSteps,
    createPipeline
  } = usePipelineStore()

  const [state, dispatch] = useReducer(reducer, initialState)

  useEffect(() => {
    const fetchStepTypes = async () => {
      try {
        const response = await stepConfigurationApi.getStepTypes()
        if (response.status === 200) {
          dispatch({ type: 'SET_STEP_TYPES', payload: response.data })
        } else {
          dispatch({ 
            type: 'SET_STEP_TYPES', 
            payload: ['data ingestion', 'data transformation', 'data visualization'] 
          })
        }
      } catch (error) {
        dispatch({ 
          type: 'SET_STEP_TYPES', 
          payload: ['data ingestion', 'data transformation', 'data visualization'] 
        })
      } finally {
        dispatch({ type: 'SET_LOADING_STEP_TYPES', payload: false })
      }
    }

    fetchStepTypes()
  }, [])

  const existingVisualizationSteps = (pipelineSteps || []).filter(
    step => step.type === 'data visualization'
  )

  const handleInputChange = e => {
    const { name, value } = e.target
    dispatch({ type: 'SET_FORM_DATA', field: name, value })
  }

  const openStepModal = (index = null) => {
    if (index !== null) {
      dispatch({ type: 'SET_CURRENT_STEP', payload: (pipelineSteps || [])[index] })
      dispatch({ type: 'SET_EDITING_STEP_INDEX', payload: index })
    } else {
      dispatch({ 
        type: 'SET_CURRENT_STEP', 
        payload: {
          name: '',
          description: '',
          type: 'data ingestion',
          step_config: {
            config_ids: [],
            connection_config: {
              extractor: {},
              loader: {}
            },
            tool: null
          }
        }
      })
      dispatch({ type: 'SET_EDITING_STEP_INDEX', payload: null })
    }
    dispatch({ type: 'SET_SHOW_STEP_MODAL', payload: true })
  }

  const closeStepModal = () => {
    dispatch({ type: 'RESET_MODAL_STATE' })
  }

  const saveStep = stepData => {
    const stepToSave = {
      ...stepData,
      step_config: {
        config_ids: stepData.step_config?.config_ids || [],
        connection_config: stepData.step_config?.connection_config || {
          extractor: {},
          loader: {}
        },
        tool: stepData.step_config?.tool || null,
        ...stepData.step_config
      }
    }

    if (state.editingStepIndex !== null) {
      stepToSave.order = state.editingStepIndex + 1
      updatePipelineStep(state.editingStepIndex, stepToSave)
      toast.success('Step updated successfully!')
    } else {
      const newOrder = (pipelineSteps || []).length + 1
      stepToSave.order = newOrder
      addPipelineStep(stepToSave)
      toast.success('Step added successfully!')
    }
    closeStepModal()
  }

  const deleteStep = index => {
    removePipelineStep(index)
    toast.success('Step removed successfully!')
  }

  const handleCreatePipeline = async () => {
    if (!state.formData.name.trim()) {
      toast.error('Please enter a pipeline name')
      return
    }

    const steps = pipelineSteps || []
    if (steps.length === 0) {
      toast.error('Please add at least one step to the pipeline')
      return
    }

    dispatch({ type: 'SET_CREATING_PIPELINE', payload: true })

    const progressToast = toast.loading(
      'Creating pipeline... This may take up 10 minutes when using Meltano. Please wait.',
      {
        duration: Infinity
      }
    )

    try {
      const unconfiguredSteps = steps.filter(step => !isStepConfigured(step))
      if (unconfiguredSteps.length > 0) {
        toast.error(
          `Please configure all steps before creating the pipeline. Unconfigured steps: ${unconfiguredSteps
            .map(s => s.name || 'Unnamed')
            .join(', ')}`
        )
        dispatch({ type: 'SET_CREATING_PIPELINE', payload: false })
        return
      }

      const pipelineData = {
        name: state.formData.name,
        description: state.formData.description,
        created_by: user?.user_id || 1,
        step_list: steps.map((step, index) => {
          return {
            name: step.name,
            description: step.description,
            step_config: {
              ...step.step_config,
              config_ids: step.step_config.config_ids || []
            },
            order: index + 1
          }
        })
      }

      const result = await createPipeline(pipelineData)

      if (result.success) {
        toast.dismiss(progressToast)
        toast.success('Pipeline created successfully!')
        clearPipelineSteps()

        let pipelineId = null

        if (typeof result.data === 'string') {
          pipelineId = result.data
        } else if (result.data && typeof result.data === 'object') {
          pipelineId =
            result.data.pipeline_id ||
            result.data.id ||
            result.data.pipelineId
        }

        if (pipelineId) {
          setTimeout(() => {
            navigate(`/view-pipeline/${pipelineId}`)
          }, 100)
        } else {
          setTimeout(() => {
            navigate('/pipeline-management')
          }, 100)
        }
      } else {
        toast.dismiss(progressToast)
        toast.error(result.error || 'Failed to create pipeline')
      }
    } catch (error) {
      toast.dismiss(progressToast)
      toast.error('An error occurred while creating the pipeline')
    } finally {
      dispatch({ type: 'SET_CREATING_PIPELINE', payload: false })
    }
  }

  const handleCancel = () => {
    clearPipelineSteps()
    navigate('/pipeline-management')
  }

  const getStepStatus = step => {
    if (!isStepConfigured(step)) {
      return { status: 'unconfigured', color: 'red', text: 'Not Configured' }
    }
    if (
      step.step_config?.table_sync_config &&
      Object.keys(step.step_config.table_sync_config).length > 0
    ) {
      return { status: 'complete', color: 'green', text: 'Complete' }
    }
    return { status: 'configured', color: 'blue', text: 'Configured' }
  }

  const generatePipelineJson = () => {
    const steps = pipelineSteps || []
    return {
      name: state.formData.name,
      description: state.formData.description,
      created_by: user?.user_id || 1,
      step_list: steps.map((step, index) => {
        return {
          name: step.name,
          description: step.description,
          step_config: {
            ...step.step_config,
            config_ids: step.step_config.config_ids || []
          },
          order: index + 1
        }
      })
    }
  }

  if (!isAdmin()) {
    return (
      <CreatePipelinePageView
        isAdmin={false}
        onNavigateToManagement={() => navigate('/pipeline-management')}
        onNavigateToDashboard={() => navigate('/dashboard')}
      />
    )
  }

  return (
    <CreatePipelinePageView
      isAdmin={true}
      formData={state.formData}
      onInputChange={handleInputChange}
      pipelineSteps={pipelineSteps || []}
      loadingStepTypes={state.loadingStepTypes}
      onAddStep={() => openStepModal()}
      onEditStep={openStepModal}
      onDeleteStep={deleteStep}
      getStepStatus={getStepStatus}
      showJsonPreview={state.showJsonPreview}
      onToggleJsonPreview={() => dispatch({ 
        type: 'SET_SHOW_JSON_PREVIEW', 
        payload: !state.showJsonPreview 
      })}
      jsonPreviewContent={generatePipelineJson()}
      onCancel={handleCancel}
      onCreatePipeline={handleCreatePipeline}
      creatingPipeline={state.creatingPipeline}
      showStepModal={state.showStepModal}
      closeStepModal={closeStepModal}
      currentStep={state.currentStep}
      saveStep={saveStep}
      isEditing={state.editingStepIndex !== null}
      existingVisualizationSteps={existingVisualizationSteps}
      stepTypes={state.stepTypes}
      allPipelineSteps={pipelineSteps || []}
    />
  )
}

export default CreatePipelinePage
