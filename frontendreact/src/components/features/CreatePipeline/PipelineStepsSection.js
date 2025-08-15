import React from 'react'
import { PlusIcon, EyeIcon, EyeSlashIcon } from '@heroicons/react/24/outline'
import StepCard from './StepCard'
import Button from '../../common/Button/Button'

const PipelineStepsSection = ({
  pipelineSteps,
  loadingStepTypes,
  onAddStep,
  onEditStep,
  onDeleteStep,
  getStepStatus,
  showJsonPreview,
  onToggleJsonPreview,
  jsonPreviewContent
}) => {
  return (
    <div className='bg-white shadow rounded-lg p-6'>
      <div className='flex items-center justify-between mb-4'>
        <h2 className='text-lg font-medium text-gray-900'>Pipeline Steps</h2>
      </div>

      {pipelineSteps.length > 0 ? (
        <div className='space-y-4'>
          {[...pipelineSteps]
            .sort((a, b) => a.order - b.order)
            .map((step, index) => (
              <StepCard
                key={index}
                step={step}
                index={index}
                onEdit={onEditStep}
                onDelete={onDeleteStep}
                getStepStatus={getStepStatus}
              />
            ))}
        </div>
      ) : (
        <div className='text-center py-8'>
          <p className='text-gray-500'>
            No steps added yet. Add your first step to get started.
          </p>
        </div>
      )}

      <div className='mt-4'>
        <Button
          onClick={onAddStep}
          disabled={loadingStepTypes}
          loading={loadingStepTypes}
          variant='primary'
          icon={PlusIcon}
          iconPosition='left'
          className='px-6 py-3 text-sm font-medium rounded-lg'
        >
          {loadingStepTypes ? 'Loading...' : 'Add Step'}
        </Button>
      </div>
    </div>
  )
}

export default PipelineStepsSection
