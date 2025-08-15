import React from 'react'

const EmptyState = ({
  totalPipelines,
  showDeprecated,
  isAdmin,
  onCreatePipeline
}) => (
  <div className='flex flex-col items-center justify-center py-12'>
    <h3 className='text-lg font-semibold mb-2'>
      {showDeprecated
        ? 'No deprecated pipelines found.'
        : 'No pipelines found.'}
    </h3>
    <p className='text-gray-500 mb-4'>
      {showDeprecated
        ? 'There are currently no deprecated pipelines.'
        : 'Get started by creating a new pipeline.'}
    </p>
  </div>
)

export default EmptyState
