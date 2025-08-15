import React from 'react'
import { ExclamationTriangleIcon } from '@heroicons/react/24/outline'
import VisualizationModal from './Visualization/VisualizationModal'
import ConfigurationModal from './ConfigurationModal'
import PipelineAccessManagement from './AccessManagement/PipelineAccessManagement'
import Button from '../../common/Button/Button'
import Modal from '../../common/Modal/Modal'

const PipelineModalsManager = ({
  pipeline,
  pipelineSteps,
  pipelineId,
  userId,
  visualizationUrl,
  visualizationCreds,
  showVisualizationModal,
  showConfigurationModal,
  showAccessManagementModal,
  showDeleteConfirmModal,
  onCloseVisualization,
  onCloseConfiguration,
  onCloseAccessManagement,
  onCloseDeleteConfirm,
  onConfirmDelete,
  onStopVisualization
}) => {

  return (
    <>
      <VisualizationModal
        showVisualizationModal={showVisualizationModal}
        visualizationUrl={visualizationUrl}
        visualizationCreds={visualizationCreds}
        onCloseVisualization={onCloseVisualization}
        onStopVisualization={onStopVisualization}
      />

      <ConfigurationModal
        showConfigurationModal={showConfigurationModal}
        onCloseConfiguration={onCloseConfiguration}
        pipelineSteps={pipelineSteps}
      />

      <Modal
        isOpen={showDeleteConfirmModal}
        onClose={onCloseDeleteConfirm}
        title="Delete Pipeline"
        size="sm"
        showCloseButton={false}
      >
        <div className='flex items-center mb-4'>
          <ExclamationTriangleIcon className='h-6 w-6 text-red-500 mr-3' />
          <p className='text-sm text-gray-600'>
            Are you sure you want to delete "{pipeline?.name}"? This action cannot be undone.
          </p>
        </div>

        <div className='flex justify-end space-x-3'>
          <Button
            onClick={onCloseDeleteConfirm}
            variant='secondary'
          >
            Cancel
          </Button>
          <Button
            onClick={onConfirmDelete}
            variant='primary'
            className='bg-red-600 hover:bg-red-700 focus:ring-red-500'
          >
            Delete Pipeline
          </Button>
        </div>
      </Modal>

      <Modal
        isOpen={showAccessManagementModal}
        onClose={onCloseAccessManagement}
        title="Pipeline Access Management"
        size="xl"
      >
        <div className='mb-4'>
          <p className='text-sm text-gray-600'>
            Manage user access and permissions for "{pipeline?.name}"
          </p>
        </div>

        <div className='bg-white rounded-lg'>
          <PipelineAccessManagement
            pipelineId={pipelineId}
            currentUserId={userId}
          />
        </div>

        <div className='flex justify-end mt-6'>
          <Button
            onClick={onCloseAccessManagement}
            variant='secondary'
          >
            Close
          </Button>
        </div>
      </Modal>
    </>
  )
}

export default PipelineModalsManager 