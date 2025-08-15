import React, { useMemo } from 'react'
import { ExclamationTriangleIcon, CogIcon } from '@heroicons/react/24/outline'
import Button from '../../common/Button/Button'
import { formatTimestamp } from '../../../utils/formatters'

const PipelineInformation = ({
  pipeline,
  pipelineSteps,
  onShowConfiguration
}) => {

  const safePipeline = useMemo(() => pipeline || {}, [pipeline])
  const safePipelineSteps = useMemo(() => pipelineSteps || [], [pipelineSteps])
  const stepCount = useMemo(() => safePipelineSteps.length, [safePipelineSteps])

  return (
    <div className='bg-white shadow rounded-lg p-6'>
      <div className='flex justify-between items-start mb-4'>
        <div className='flex items-center space-x-3'>
          <h2 className='text-lg font-medium text-gray-900'>
            Pipeline Information
          </h2>
          {safePipeline.is_deprecated && (
            <span className='inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800'>
              <ExclamationTriangleIcon className='h-3 w-3 mr-1' />
              Deprecated
            </span>
          )}
        </div>
        <Button
          onClick={onShowConfiguration}
          icon={CogIcon}
          iconPosition='left'
        >
          View Configuration
        </Button>
      </div>
      <div className='grid grid-cols-1 md:grid-cols-3 gap-6'>
        <div>
          <dt className='text-sm font-medium text-gray-500'>Number of Steps</dt>
          <dd className='mt-1 text-sm text-gray-900'>
            {stepCount} {stepCount === 1 ? 'step' : 'steps'}
          </dd>
        </div>
        <div>
          <dt className='text-sm font-medium text-gray-500'>Created At</dt>
          <dd className='mt-1 text-sm text-gray-900'>
            {formatTimestamp(safePipeline.created_at)}
          </dd>
        </div>
        <div>
          <dt className='text-sm font-medium text-gray-500'>Updated At</dt>
          <dd className='mt-1 text-sm text-gray-900'>
            {formatTimestamp(safePipeline.updated_at)}
          </dd>
        </div>
      </div>
    </div>
  )
}

export default PipelineInformation
