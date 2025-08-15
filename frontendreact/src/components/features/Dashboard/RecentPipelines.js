import React from 'react'
import { useNavigate } from 'react-router-dom'
import { PlusIcon } from '@heroicons/react/24/outline'
import useAuthStore from '../../../store/authStore'
import Button from '../../common/Button/Button'
import { getStatusIcon, getStatusColor } from '../../../utils/statusUtils'
import { formatDate } from '../../../utils/formatters'

const RecentPipelines = ({ pipelines, isLoading }) => {
  const navigate = useNavigate()
  const { isAdmin } = useAuthStore()



  if (isLoading) {
    return (
      <div className='bg-white shadow rounded-lg border border-secondary-100'>
        <div className='px-4 py-5 sm:p-6'>
          <h3 className='text-lg leading-6 font-medium text-primary-900 mb-4'>
            Recent Pipelines
          </h3>
          <div className='flex justify-center py-8'>
            <div className='animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500'></div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className='bg-white shadow rounded-lg border border-secondary-100'>
      <div className='px-4 py-5 sm:p-6'>
        <h3 className='text-lg leading-6 font-medium text-primary-900 mb-4'>
          Recent Pipelines
        </h3>

        {pipelines.length > 0 ? (
          <div className='flow-root'>
            <ul className='-my-5 divide-y divide-gray-200'>
              {pipelines.map(pipeline => (
                <li key={pipeline.pipeline_id} className='py-4'>
                  <div className='flex items-center space-x-4'>
                    <div className='flex-shrink-0'>
                      {(() => {
                        const IconComponent = getStatusIcon(pipeline.status)
                        const colorClass = pipeline.status === 'running' ? 'text-green-500' : 
                                          pipeline.status === 'broken' ? 'text-red-500' :
                                          pipeline.status === 'stopped' ? 'text-yellow-500' : 'text-gray-500'
                        return <IconComponent className={`h-5 w-5 ${colorClass}`} />
                      })()}
                    </div>
                    <div className='flex-1 min-w-0'>
                      <Button
                        onClick={() => navigate(`/view-pipeline/${pipeline.pipeline_id}`)}
                        className='text-left w-full hover:bg-gray-50 rounded-md p-2 transition-colors'
                        variant='text'
                      >
                        <p className='text-sm font-medium text-gray-900 truncate'>
                          {pipeline.name}
                        </p>
                        <p className='text-sm text-gray-600 truncate'>
                        {pipeline.step_count} steps 
                        </p>
                        <p className='text-sm text-gray-600 truncate'>
                        Created by{' '} {pipeline.username}
                        </p>
                      </Button>
                    </div>
                    <div className='flex-shrink-0'>
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(
                          pipeline.status
                        )}`}
                      >
                        {pipeline.status}
                      </span>
                    </div>
                    <div className='flex-shrink-0 text-sm text-secondary-500'>
                      {formatDate(pipeline.created_at)}
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        ) : (
          <div className='text-center py-8'>
            <p className='text-secondary-500'>
              {isAdmin()
                ? 'No pipelines found. Create your first pipeline to get started!'
                : 'No pipelines found. Contact an administrator to create pipelines.'}
            </p>
            {isAdmin() && (
              <Button
                onClick={() => navigate('/create-pipeline')}
                className='mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-primary-700 bg-primary-100 hover:bg-primary-200'
                icon={PlusIcon}
                iconPosition='left'
              >
                Create Pipeline
              </Button>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default RecentPipelines
