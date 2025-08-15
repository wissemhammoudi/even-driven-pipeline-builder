import React from 'react'
import Modal from '../../common/Modal/Modal'
import Button from '../../common/Button/Button'

const ConfigModal = ({ isOpen, selectedConfig, onClose }) => {
  if (!isOpen || !selectedConfig) return null

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={`${selectedConfig.plugin_name} - Configuration Details`}
      size="md"
    >
      <div className='space-y-4'>
        <div>
          <h4 className='text-sm font-medium text-gray-700 mb-2'>
            Plugin Information
          </h4>
          <div className='bg-gray-50 p-3 rounded-md'>
            <div className='grid grid-cols-2 gap-4 text-sm'>
              <div>
                <span className='font-medium'>Plugin Name:</span>{' '}
                {selectedConfig.plugin_name}
              </div>
              <div>
                <span className='font-medium'>Plugin Type:</span>{' '}
                {selectedConfig.plugin_type}
              </div>
              <div>
                <span className='font-medium'>Step Type:</span>{' '}
                {selectedConfig.type}
              </div>
              <div>
                <span className='font-medium'>Config ID:</span>{' '}
                {selectedConfig.step_config_id}
              </div>
            </div>
          </div>
        </div>

        <div>
          <h4 className='text-sm font-medium text-gray-700 mb-2'>
            Configuration
          </h4>
          <div className='bg-gray-50 p-3 rounded-md'>
            <pre className='text-sm text-gray-800 whitespace-pre-wrap'>
              {JSON.stringify(selectedConfig.config, null, 2)}
            </pre>
          </div>
        </div>
      </div>
      <div className='flex justify-end mt-6'>
        <Button
          onClick={onClose}
          variant='secondary'
        >
          Close
        </Button>
      </div>
    </Modal>
  )
}

export default ConfigModal
