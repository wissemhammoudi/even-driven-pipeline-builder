import React from 'react'
import PropTypes from 'prop-types'
import { PencilIcon, TrashIcon } from '@heroicons/react/24/outline'
import Button from '../../common/Button/Button'
import Card from '../../common/Card/Card'

const StepCard = ({ step, index, onEdit, onDelete, getStepStatus }) => {
  const stepStatus = getStepStatus(step)

  return (
    <Card className='mb-0'>
      <div className='flex items-center justify-between'>
        <div className='flex-1'>
          <div className='flex items-center space-x-3'>
            <span className='inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800'>
              Step {index + 1}
            </span>
            <h3 className='text-sm font-medium text-gray-900'>
              {step.name || 'Unnamed Step'}
            </h3>
            <span className='inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800'>
              {step.type}
            </span>
            <span
              className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                stepStatus.color === 'red' ? 'bg-red-100 text-red-800' :
                stepStatus.color === 'green' ? 'bg-green-100 text-green-800' :
                stepStatus.color === 'blue' ? 'bg-blue-100 text-blue-800' :
                'bg-gray-100 text-gray-800'
              }`}
            >
              {stepStatus.text}
            </span>
          </div>
          {step.description && (
            <p className='mt-1 text-sm text-gray-500'>{step.description}</p>
          )}
          {step.step_config?.tool && (
            <p className='mt-1 text-sm text-gray-600'>
              Tool: <span className='font-medium'>{step.step_config.tool}</span>
            </p>
          )}
        </div>
        <div className='flex items-center space-x-2'>
          <Button
            onClick={() => onEdit(index)}
            icon={PencilIcon}
            variant='secondary'
            className='p-1 rounded-full text-gray-400 hover:text-gray-500 focus:ring-primary-500'
            title='Edit Step'
          />
          <Button
            onClick={() => onDelete(index)}
            icon={TrashIcon}
            variant='secondary'
            className='p-1 rounded-full text-gray-400 hover:text-red-500 focus:ring-red-500'
            title='Delete Step'
          />
        </div>
      </div>
    </Card>
  )
}

StepCard.propTypes = {
  step: PropTypes.shape({
    name: PropTypes.string,
    type: PropTypes.string.isRequired,
    description: PropTypes.string,
    step_config: PropTypes.shape({
      tool: PropTypes.string
    })
  }).isRequired,
  index: PropTypes.number.isRequired,
  onEdit: PropTypes.func.isRequired,
  onDelete: PropTypes.func.isRequired,
  getStepStatus: PropTypes.func.isRequired
}

StepCard.defaultProps = {
  step: {
    name: '',
    description: '',
    step_config: {}
  }
}

export default StepCard
