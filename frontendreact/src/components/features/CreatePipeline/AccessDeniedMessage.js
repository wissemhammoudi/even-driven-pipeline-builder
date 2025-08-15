import React from 'react'
import { ShieldExclamationIcon } from '@heroicons/react/24/outline'
import Button from '../../common/Button/Button'

const AccessDeniedMessage = ({
  onNavigateToManagement,
  onNavigateToDashboard
}) => {
  return (
    <div className='flex flex-col items-center justify-center min-h-[400px] space-y-6'>
      <ShieldExclamationIcon className='h-20 w-20 text-red-500' />
      <div className='text-center space-y-4'>
        <h1 className='text-3xl font-bold text-gray-900'>
          Admin Access Required
        </h1>
        <div className='max-w-md mx-auto space-y-3'>
          <p className='text-lg text-gray-700 font-medium'>
            Pipeline creation is restricted to administrators only.
          </p>
          <p className='text-gray-600'>
            Only users with admin privileges can create new data pipelines. This
            ensures proper security and access control.
          </p>
          <div className='bg-yellow-50 border border-yellow-200 rounded-lg p-4 mt-4'>
            <p className='text-sm text-yellow-800'>
              <strong>Need to create a pipeline?</strong> Contact your system
              administrator to request admin access or have them create the
              pipeline for you.
            </p>
          </div>
        </div>
      </div>
      <div className='flex space-x-4'>
        <Button
          onClick={onNavigateToManagement}
          variant='primary'
        >
          Back to Pipeline Management
        </Button>
        <Button
          onClick={onNavigateToDashboard}
          variant='secondary'
        >
          Go to Dashboard
        </Button>
      </div>
    </div>
  )
}

export default AccessDeniedMessage
