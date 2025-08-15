import React, { useMemo } from 'react'
import { XCircleIcon, ArrowLeftIcon, PlayIcon, TrashIcon, ComputerDesktopIcon, UsersIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline'
import PipelineModalsManager from '../../components/features/ViewPipelinePage/PipelineModalsManager'
import PageHeader from '../../components/common/PageHeader'
import PipelineInformation from '../../components/features/ViewPipelinePage/PipelineInformation'
import PipelineAnalytics from '../../components/features/ViewPipelinePage/Analytics/PipelineAnalytics'
import PipelineRunsTable from '../../components/features/ViewPipelinePage/PipelineRunsTable'
import Button from '../../components/common/Button/Button'
import SchemaChangeAlert from '../../components/features/ViewPipelinePage/SchemaChangeAlert'
import { stepHasType } from '../../utils/pipeline'
import { useViewPipelinePage } from './useViewPipelinePage'

const ViewPipelinePage = () => {
  const {
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
  } = useViewPipelinePage()

  const hasVisualizationStep = useMemo(
    () => safePipelineSteps.some(step => stepHasType(step, ['data visualization', 'DATA_VISUALIZATION'])),
    [safePipelineSteps]
  )

  const hasIngestOrTransformStep = useMemo(
    () => safePipelineSteps.some(step => stepHasType(step, [
      'data transformation',
      'data ingestion',
      'DATA_TRANSFORMATION',
      'DATA_INGESTION'
    ])),
    [safePipelineSteps]
  )

  const hasAccess = useMemo(() => {
    return user?.role === 'admin' || safePermissions.can_view_pipeline
  }, [user?.role, safePermissions.can_view_pipeline])

  const isLoadingPermissions = useMemo(() => {
    return safePermissions.loading === true
  }, [safePermissions.loading])

  if (isLoadingData) {
    return (
      <div className='flex justify-center py-12'>
        <div className='animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500'></div>
      </div>
    )
  }

  if (!isLoadingData && !safePipeline.pipeline_id) {
    return (
      <div className='text-center py-12'>
        <p className='text-gray-500'>Pipeline not found</p>
        <Button
          onClick={handleBackToDashboard}
          className='mt-4'
          icon={ArrowLeftIcon}
          iconPosition='left'
        >
          Back to Dashboard
        </Button>
      </div>
    )
  }

  if (!hasAccess && !isLoadingPermissions) {
    return (
      <div className='text-center py-12'>
        <div className='max-w-md mx-auto'>
          <div className='flex justify-center mb-4'>
            <XCircleIcon className='h-12 w-12 text-red-500' />
          </div>
          <h2 className='text-lg font-medium text-gray-900 mb-2'>
            Access Denied
          </h2>
          <p className='text-gray-500 mb-4'>
            You don't have permission to view this pipeline. Please contact the
            pipeline owner or administrator for access.
          </p>
          <Button
            onClick={handleBackToPipelines}
            icon={ArrowLeftIcon}
            iconPosition='left'
          >
            Back to Pipelines
          </Button>
        </div>
      </div>
    )
  }

  return (
    <>
      <SchemaChangeAlert breakingChanges={breakingChanges} schemaChanges={schemaChanges} />
      <div className='space-y-6'>
        <PageHeader
          title={safePipeline.name}
          onBackClick={handleBackToDashboard}
          backIcon={ArrowLeftIcon}
          actions={
            <>
              {!safePipeline.is_deprecated && (
                <>
                  {hasIngestOrTransformStep && safePermissions.can_start_pipeline && (
                    <Button
                      onClick={handleRunPipeline}
                      disabled={isRunning || (breakingChanges && breakingChanges.length > 0)}
                      icon={PlayIcon}
                      iconPosition='left'
                    >
                      {isRunning ? 'Starting...' : 'Start Pipeline'}
                    </Button>
                  )}

                  {hasVisualizationStep &&
                    !visualizationUrl &&
                    safePermissions.can_start_visualization && (
                      <Button
                        onClick={handleStartVisualization}
                        disabled={isVisualizationRunning}
                        variant='secondary'
                        icon={ComputerDesktopIcon}
                        iconPosition='left'
                      >
                        {isVisualizationRunning
                          ? 'Starting...'
                          : 'Start Visualization'}
                      </Button>
                    )}

                  {safePermissions.can_manage_access && (
                    <Button
                      onClick={() => setShowAccessManagementModal(true)}
                      variant='secondary'
                      icon={UsersIcon}
                      iconPosition='left'
                    >
                      Manage Access
                    </Button>
                  )}

                  {safePermissions.can_delete_pipeline && (
                    <Button
                      onClick={handleDeleteConfirm}
                      variant='secondary'
                      icon={TrashIcon}
                      iconPosition='left'
                      className='border-red-300 text-red-700 hover:bg-red-50 focus:ring-red-500'
                    >
                      Delete
                    </Button>
                  )}
                </>
              )}

              {safePipeline.is_deprecated && (
                <div className='inline-flex items-center px-4 py-2 border border-yellow-300 shadow-sm text-sm font-medium rounded-md text-yellow-700 bg-yellow-50'>
                  <ExclamationTriangleIcon className='h-4 w-4 mr-2' />
                  Pipeline Deprecated
                </div>
              )}
            </>
          }
        />

        <PipelineInformation
          pipeline={safePipeline}
          pipelineSteps={safePipelineSteps}
          onShowConfiguration={() => setShowConfigurationModal(true)}
        />

        <PipelineAnalytics
          pipelineId={pipelineId}
          days={30}
          refreshTrigger={analyticsRefreshTrigger}
        />

        <PipelineRunsTable pipelineRuns={safePipelineRuns} />
      </div>

      <PipelineModalsManager
        pipeline={safePipeline}
        pipelineSteps={safePipelineSteps}
        pipelineId={pipelineId}
        userId={user?.user_id}
        visualizationUrl={visualizationUrl}
        visualizationCreds={visualizationCreds}
        showVisualizationModal={showVisualizationModal}
        showConfigurationModal={showConfigurationModal}
        showAccessManagementModal={showAccessManagementModal}
        showDeleteConfirmModal={showDeleteConfirmModal}
        onCloseVisualization={handleCloseVisualization}
        onCloseConfiguration={() => setShowConfigurationModal(false)}
        onCloseAccessManagement={() => setShowAccessManagementModal(false)}
        onCloseDeleteConfirm={handleCloseDeleteConfirm}
        onConfirmDelete={handleDeletePipeline}
        onStopVisualization={stopVisualization}
      />
    </>
  )
}

export default ViewPipelinePage
