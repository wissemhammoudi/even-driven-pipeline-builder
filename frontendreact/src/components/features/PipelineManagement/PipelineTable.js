import React from 'react'
import PipelineRow from './PipelineRow'

const PipelineTable = ({
  pipelines,
  title,
  onView,
  onDelete,
  hasPermission,
  actionLoading,
  permissionsLoading,
  isAdmin,
  isDeprecated = false
}) => {
  if (pipelines.length === 0) {
    return (
      <div className='text-center py-8'>
        <p className='text-gray-500'>
          {isDeprecated
            ? 'No deprecated pipelines found.'
            : 'No pipelines found.'}
        </p>
      </div>
    )
  }

  return (
    <div className='space-y-4'>
      <h3 className='text-lg font-medium text-gray-900'>{title}</h3>
      <div className='overflow-hidden'>
        <table className='min-w-full divide-y divide-gray-200'>
          <thead className='bg-gray-50'>
            <tr>
              <th className='px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider'>
                Pipeline
              </th>
              <th className='px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider'>
                Created
              </th>
              <th className='px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider'>
                Actions
              </th>
            </tr>
          </thead>
          <tbody className='bg-white divide-y divide-gray-200'>
            {pipelines.map(pipeline => (
              <PipelineRow
                key={pipeline.pipeline_id}
                pipeline={pipeline}
                onView={onView}
                onDelete={onDelete}
                hasPermission={hasPermission}
                actionLoading={actionLoading}
                permissionsLoading={permissionsLoading}
                isAdmin={isAdmin}
              />
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default PipelineTable
