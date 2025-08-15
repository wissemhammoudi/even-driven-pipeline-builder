import React from 'react'
import Modal from '../../common/Modal/Modal'

const ConfigurationModal = ({
  showConfigurationModal,
  onCloseConfiguration,
  pipelineSteps
}) => {
  const formatTimestamp = timestamp => {
    if (!timestamp) return 'N/A'
    return timestamp.replace('T', ' ').split('.')[0]
  }

  const renderStepConfig = config => {
    if (!config) {
      return <p className='text-gray-500 italic'>No configuration available.</p>
    }

    const renderValue = value => {
      if (value === null || value === undefined) {
        return <span className='text-gray-400 italic'>null</span>
      }

      if (
        typeof value === 'string' ||
        typeof value === 'number' ||
        typeof value === 'boolean'
      ) {
        return <span>{String(value)}</span>
      }

      if (typeof value === 'object' && value !== null) {
        if (value.type && value.msg) {
          return (
            <span className='text-red-600 text-sm'>
              {value.msg} {value.input && `(input: ${value.input})`}
            </span>
          )
        }

        if (React.isValidElement(value)) {
          return value
        }

        if (value instanceof Date) {
          return <span>{value.toISOString()}</span>
        }

        if (typeof value === 'function') {
          return <span className='text-gray-400 italic'>[Function]</span>
        }

        try {
          return (
            <div className='ml-4 border-l-2 border-gray-200 pl-3'>
              {Object.entries(value).map(([subKey, subValue]) => (
                <div key={subKey} className='mb-2'>
                  <span className='font-medium text-gray-700'>
                    {subKey
                      .replace(/_/g, ' ')
                      .replace(/\b\w/g, l => l.toUpperCase())}
                    :
                  </span>{' '}
                  {renderValue(subValue)}
                </div>
              ))}
            </div>
          )
        } catch (error) {
          return (
            <span className='text-red-600 text-sm'>
              [Error rendering object]
            </span>
          )
        }
      }

      if (typeof value === 'object' && value !== null) {
        return <span className='text-gray-400 italic'>[Object]</span>
      }

      if (Array.isArray(value)) {
        return (
          <ul className='list-disc list-inside'>
            {value.map((item, index) => (
              <li key={index} className='text-sm text-gray-600'>
                {renderValue(item)}
              </li>
            ))}
          </ul>
        )
      }

      return <span>{String(value)}</span>
    }

    return (
      <div className='space-y-3'>
        {Object.entries(config).map(([key, value]) => {
          const formattedKey = key
            .replace(/_/g, ' ')
            .replace(/\b\w/g, l => l.toUpperCase())

          return (
            <div
              key={key}
              className='border-b border-gray-100 pb-2 last:border-b-0'
            >
              <p className='font-medium text-gray-700 mb-1'>{formattedKey}:</p>
              <div className='text-sm text-gray-600'>{renderValue(value)}</div>
            </div>
          )
        })}
      </div>
    )
  }

  return (
    <Modal
      isOpen={showConfigurationModal}
      onClose={onCloseConfiguration}
      title="Pipeline Configuration"
      size="xl"
    >

        <div className='space-y-6'>
          {pipelineSteps.length === 0 ? (
            <p className='text-gray-500 text-center py-8'>No steps found.</p>
          ) : (
            pipelineSteps.map((step, index) => (
              <div
                key={step.step_id}
                className='border border-gray-200 rounded-lg p-6'
              >
                <h4 className='text-lg font-medium text-gray-900 mb-3'>
                  Step {index + 1}: {step.name}
                </h4>
                <p className='text-sm text-gray-600 mb-4'>
                  {step.description || 'No description'}
                </p>

                <div className='grid grid-cols-1 md:grid-cols-2 gap-4 mb-4'>
                  <div>
                    <span className='text-sm font-medium text-gray-500'>
                      Created At:
                    </span>
                    <span className='ml-2 text-sm text-gray-900'>
                      {formatTimestamp(step.created_at)}
                    </span>
                  </div>
                  <div>
                    <span className='text-sm font-medium text-gray-500'>
                      Updated At:
                    </span>
                    <span className='ml-2 text-sm text-gray-900'>
                      {formatTimestamp(step.updated_at)}
                    </span>
                  </div>
                </div>

                <div className='bg-gray-50 rounded-md p-4'>
                  <h5 className='text-sm font-medium text-gray-700 mb-3'>
                    Configuration:
                  </h5>
                  <div className='text-sm text-gray-800'>
                    {renderStepConfig(step.step_config)}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>

        <div className='flex justify-end mt-6'>
          <button
            onClick={onCloseConfiguration}
            className='px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500'
          >
            Close
          </button>
        </div>
    </Modal>
  )
}

export default ConfigurationModal
