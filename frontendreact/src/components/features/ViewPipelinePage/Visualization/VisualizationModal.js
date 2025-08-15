import React from 'react'
import CredentialsBar from './CredentialsBar'
import VisualizationIframe from './VisualizationIframe'
import Modal from '../../../common/Modal/Modal'

const VisualizationModal = ({
  showVisualizationModal,
  visualizationUrl,
  visualizationCreds,
  onCloseVisualization,
  onStopVisualization
}) => {
  if (!showVisualizationModal || !visualizationUrl) return null

  return (
    <Modal
      isOpen={showVisualizationModal}
      onClose={onCloseVisualization}
      title="Superset Visualization"
      size="full"
      className="h-[95vh] flex flex-col"
    >
      <div className='flex-1 flex flex-col bg-gray-100 rounded-md overflow-hidden'>
        <CredentialsBar 
          credentials={visualizationCreds}
          visualizationUrl={visualizationUrl}
        />
        
        <div className='flex-1 min-h-0'>
          <VisualizationIframe 
            visualizationUrl={visualizationUrl}
          />
        </div>
      </div>

      <div className='flex justify-end mt-3 space-x-3 flex-shrink-0'>
        <button
          onClick={onStopVisualization}
          className='px-4 py-2 border border-red-300 rounded-md shadow-sm text-sm font-medium text-red-700 bg-white hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition-colors'
        >
          Stop Visualization
        </button>
        <button
          onClick={onCloseVisualization}
          className='px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors'
        >
          Close
        </button>
      </div>
    </Modal>
  )
}

export default VisualizationModal 