import React from 'react'
import { EyeIcon, EyeSlashIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline'
import { getTransformationIcon } from './utils'
import Button from '../../common/Button/Button'
import TransformationCard from './TransformationCard'
import { StepTypeEnum } from '../CreatePipeline/StepWizard/utils'
const TransformationsSection = ({
  selectedTool,
  selectedType,
  transformations,
  showTransformations,
  onToggleTransformations
}) => {
  if (selectedType !== StepTypeEnum.DATA_TRANSFORMATION || transformations.length === 0) {
    return null
  }

  return (
    <div className='bg-white shadow rounded-lg p-6'>
      <div className='flex justify-between items-center mb-4'>
        <h2 className='text-lg font-medium text-gray-900'>
          Supported Transformations for{' '}
          <span className='text-primary font-semibold'>{selectedTool}</span>
        </h2>

        <Button
          onClick={onToggleTransformations}
          variant='secondary'
          icon={showTransformations ? EyeSlashIcon : EyeIcon}
          iconPosition='left'
          className='px-3 py-2 text-sm'
        >
          {showTransformations ? 'Hide Transformations' : `Show Transformations (${transformations.length})`}
        </Button>
      </div>

      {showTransformations ? (
        <div className='grid grid-cols-1 lg:grid-cols-2 gap-6'>
          {transformations.map((transformation, index) => (
            <TransformationCard key={index} transformation={transformation} />
          ))}
        </div>
      ) : (
        <div className='mt-4 p-4 bg-gray-100 border border-gray-200 rounded-md'>
          <div className='flex items-center'>
            <ExclamationTriangleIcon className='h-5 w-5 text-gray-400 mr-2' />
            <span className='text-sm text-gray-700'>
              There are {transformations.length} transformation type(s)
              available. Click "Show Transformations" to view them.
            </span>
          </div>
        </div>
      )}
    </div>
  )
}

export default TransformationsSection
