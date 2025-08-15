import { useEffect, useState, useCallback, useMemo } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import useAuthStore from '../../store/authStore'
import usePipelineStore from '../../store/pipelineStore'
import { schemaChangeAPI } from '../../utils/api'

export function useViewPipelinePage() {
  const { pipelineId } = useParams()
  const navigate = useNavigate()
  const { user } = useAuthStore()

  const {
    currentPipeline: pipeline,
    currentPipelineSteps: pipelineSteps,
    currentPipelineRuns: pipelineRuns,
    isLoadingPipeline: isLoadingData,
    permissions,
    isRunning,
    isVisualizationRunning,
    visualizationUrl,
    visualizationCreds,
    loadPipelineData,
    loadPermissions,
    runPipeline,
    startVisualization,
    stopVisualization,
    deletePipeline,
    resetCurrentPipeline
  } = usePipelineStore()

  const [showVisualizationModal, setShowVisualizationModal] = useState(false)
  const [showConfigurationModal, setShowConfigurationModal] = useState(false)
  const [showAccessManagementModal, setShowAccessManagementModal] = useState(false)
  const [showDeleteConfirmModal, setShowDeleteConfirmModal] = useState(false)
  const [analyticsRefreshTrigger, setAnalyticsRefreshTrigger] = useState(0)
  const [schemaChanges, setSchemaChanges] = useState([])
  const [breakingChanges, setBreakingChanges] = useState([])
  const [isBlockedByBreakingChange, setIsBlockedByBreakingChange] = useState(false)
  const [showBreakingChanges, setShowBreakingChanges] = useState(false)

  const safePipeline = useMemo(() => pipeline || {}, [pipeline])
  const safePipelineSteps = useMemo(() => pipelineSteps || [], [pipelineSteps])
  const safePipelineRuns = useMemo(() => pipelineRuns || [], [pipelineRuns])
  const safePermissions = useMemo(() => permissions || {}, [permissions])

  useEffect(() => {
    if (pipelineId && user?.user_id) {
      loadPipelineData(pipelineId, user)
      loadPermissions(pipelineId, user.user_id)
    }
    if (pipelineId) {
      schemaChangeAPI.getSchemaChanges(pipelineId)
        .then(res => setSchemaChanges(res.data || []))
        .catch(() => setSchemaChanges([]))
      schemaChangeAPI.getBreakingChanges(pipelineId)
        .then(res => {
          setBreakingChanges(res.data || [])
          setIsBlockedByBreakingChange((res.data || []).length > 0)
        })
        .catch(() => {
          setBreakingChanges([])
          setIsBlockedByBreakingChange(false)
        })
    }
    return () => resetCurrentPipeline()
  }, [pipelineId, user?.user_id, loadPipelineData, loadPermissions, resetCurrentPipeline])

  const handleRunPipeline = useCallback(async () => {
    if (!safePipeline.pipeline_id || !user?.user_id) return
    const result = await runPipeline(safePipeline.pipeline_id, user.user_id)
    if (result?.success) {
      setAnalyticsRefreshTrigger(prev => prev + 1)
    }
  }, [safePipeline.pipeline_id, user?.user_id, runPipeline])

  const handleStartVisualization = useCallback(async () => {
    if (!safePipeline.pipeline_id || !user?.user_id) return
    const result = await startVisualization(safePipeline.pipeline_id, user.user_id)
    if (result?.success) {
      setShowVisualizationModal(true)
    }
  }, [safePipeline.pipeline_id, user?.user_id, startVisualization])

  const handleDeletePipeline = useCallback(async () => {
    if (!safePipeline.pipeline_id) return
    const result = await deletePipeline(safePipeline.pipeline_id)
    if (result?.success) {
      navigate('/pipeline-management')
    }
  }, [safePipeline.pipeline_id, deletePipeline, navigate])

  const handleDeleteConfirm = useCallback(() => {
    setShowDeleteConfirmModal(true)
  }, [])

  const handleCloseVisualization = useCallback(() => {
    setShowVisualizationModal(false)
    stopVisualization()
  }, [stopVisualization])

  const handleCloseDeleteConfirm = useCallback(() => {
    setShowDeleteConfirmModal(false)
  }, [])

  const handleBackToDashboard = useCallback(() => {
    navigate('/dashboard')
  }, [navigate])

  const handleBackToPipelines = useCallback(() => {
    navigate('/pipeline-management')
  }, [navigate])

  return {
    pipelineId,
    user,
    safePipeline,
    safePipelineSteps,
    safePipelineRuns,
    safePermissions,
    isLoadingData,
    isRunning,
    isVisualizationRunning,
    visualizationUrl,
    visualizationCreds,
    showVisualizationModal,
    setShowVisualizationModal,
    showConfigurationModal,
    setShowConfigurationModal,
    showAccessManagementModal,
    setShowAccessManagementModal,
    showDeleteConfirmModal,
    setShowDeleteConfirmModal,
    analyticsRefreshTrigger,
    setAnalyticsRefreshTrigger,
    schemaChanges,
    breakingChanges,
    isBlockedByBreakingChange,
    showBreakingChanges,
    setShowBreakingChanges,
    handleRunPipeline,
    handleStartVisualization,
    handleDeletePipeline,
    handleDeleteConfirm,
    handleCloseVisualization,
    handleCloseDeleteConfirm,
    stopVisualization,
    handleBackToDashboard,
    handleBackToPipelines
  }
} 