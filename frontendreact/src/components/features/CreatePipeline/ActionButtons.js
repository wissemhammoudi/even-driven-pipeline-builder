import React from 'react'
import Button from '../../common/Button/Button'

const ActionButtons = ({
  onCancel,
  onCreatePipeline,
  creatingPipeline,
  pipelineSteps,
  formData
}) => {
  const isDisabled =
    creatingPipeline || pipelineSteps.length === 0 || !formData.name.trim()

  return (
    <div className='flex justify-end space-x-4'>
      <Button
        onClick={onCancel}
        variant='secondary'
      >
        Cancel
      </Button>
      <Button
        onClick={onCreatePipeline}
        disabled={isDisabled}
        loading={creatingPipeline}
        variant='primary'
      >
        {creatingPipeline ? (
          <>
            Creating Pipeline...
          </>
        ) : (
          'Create Pipeline'
        )}
      </Button>
    </div>
  )
}

export default ActionButtons
