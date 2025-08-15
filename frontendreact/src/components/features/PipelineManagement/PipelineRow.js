import React, { useState } from 'react'
import {
  EyeIcon,
  TrashIcon,
  ClockIcon,
  XCircleIcon,
  ExclamationTriangleIcon,
  ArchiveBoxIcon
} from '@heroicons/react/24/outline'
import Button from '../../common/Button/Button'
import DeleteConfirmModal from '../../common/Modal/DeleteConfirmModal'

const PipelineRow = ({
  pipeline,
  onView,
  onDelete,
  hasPermission,
  actionLoading,
  permissionsLoading,
  isAdmin
}) => {
  const getStatusIcon = (status, isDeprecated) => {
    if (isDeprecated) {
      return <ArchiveBoxIcon className='h-5 w-5 text-gray-500' />
    }
    switch (status) {
      case 'BROKEN':
        return <XCircleIcon className='h-5 w-5 text-red-500' />
      case 'STOPPED':
        return <ExclamationTriangleIcon className='h-5 w-5 text-yellow-500' />
      case 'RUNNING':
        return <ClockIcon className='h-5 w-5 text-blue-500' />
      default:
        return null
    }
  }

  const canDeletePipeline = hasPermission(
    pipeline.pipeline_id,
    'can_delete_pipeline'
  )
  const isLoading = actionLoading[pipeline.pipeline_id]

  const [showDeleteModal, setShowDeleteModal] = useState(false)

  return (
    <>
      <tr key={pipeline.pipeline_id} className='hover:bg-gray-50'>
        <td className='px-6 py-4 whitespace-nowrap'>
          <div className='flex items-center'>
            <div className='flex-shrink-0 h-10 w-10'>
              {getStatusIcon(pipeline.status, pipeline.is_deprecated)}
            </div>
            <div className='ml-4'>
              <div className='text-sm font-medium text-gray-900'>
                {pipeline.name}
              </div>
              <div className='text-sm text-gray-500'>
                {pipeline.description || 'No description'}
              </div>
            </div>
          </div>
        </td>
        <td className='px-6 py-4 whitespace-nowrap text-sm text-gray-500'>
          {new Date(pipeline.created_at).toLocaleDateString()}
        </td>
        <td className='px-6 py-4 whitespace-nowrap text-right text-sm font-medium'>
          <div className='flex items-center justify-end space-x-2'>
            <Button
              onClick={() => onView(pipeline.pipeline_id)}
              className='p-1 border border-transparent rounded-full text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500'
              title='View Pipeline'
              variant='text'
              icon={EyeIcon}
              iconPosition='left'
            />

            {!pipeline.is_deprecated && (
              <>
                {canDeletePipeline && (
                  <Button
                    onClick={() => setShowDeleteModal(true)}
                    loading={isLoading}
                    disabled={isLoading}
                    className='p-1 border border-transparent rounded-full text-gray-400 hover:text-red-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50 disabled:cursor-not-allowed'
                    title='Delete Pipeline'
                    variant='text'
                    icon={TrashIcon}
                    iconPosition='left'
                  />
                )}
              </>
            )}

            {pipeline.is_deprecated && (
              <div className='text-sm text-gray-500 italic'>View only</div>
            )}

            {permissionsLoading && (
              <div className='animate-spin rounded-full h-4 w-4 border-b-2 border-gray-400'></div>
            )}
          </div>
        </td>
      </tr>
      <DeleteConfirmModal
        isOpen={showDeleteModal}
        onClose={() => setShowDeleteModal(false)}
        onConfirm={() => {
          setShowDeleteModal(false)
          onDelete(pipeline.pipeline_id, pipeline.name)
        }}
        itemName={pipeline.name}
        loading={isLoading}
      />
    </>
  )
}

export default PipelineRow
