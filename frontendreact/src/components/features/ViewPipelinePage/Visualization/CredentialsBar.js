import React, { useState } from 'react'
import { EyeIcon, EyeSlashIcon, ComputerDesktopIcon } from '@heroicons/react/24/outline'

const CredentialsBar = ({ credentials, visualizationUrl }) => {
  const [showCredentials, setShowCredentials] = useState(false)

  if (!credentials) return null

  return (
    <div className='bg-blue-50 border-b border-blue-200 p-3 flex-shrink-0'>
      <div className='flex items-center justify-between'>
        <div className='flex items-center space-x-4 text-sm'>
          <span className='font-medium text-blue-900'>
            Login Credentials:
          </span>
          <span>
            Username:{' '}
            <code className='bg-blue-100 px-2 py-1 rounded text-xs'>
              {credentials.username || 'N/A'}
            </code>
          </span>
          <span>
            Password:{' '}
            <code className='bg-blue-100 px-2 py-1 rounded text-xs'>
              {showCredentials
                ? credentials.password || 'N/A'
                : '••••••••'}
            </code>
          </span>
        </div>
        <div className='flex items-center space-x-2'>
          <button
            onClick={() => setShowCredentials(!showCredentials)}
            className='inline-flex items-center px-2 py-1 text-xs font-medium text-blue-700 bg-blue-100 rounded hover:bg-blue-200 transition-colors'
          >
            {showCredentials ? (
              <>
                <EyeSlashIcon className='h-3 w-3 mr-1' />
                Hide
              </>
            ) : (
              <>
                <EyeIcon className='h-3 w-3 mr-1' />
                Show
              </>
            )}
          </button>
          <a
            href={visualizationUrl}
            target='_blank'
            rel='noopener noreferrer'
            className='inline-flex items-center px-2 py-1 text-xs font-medium text-blue-700 bg-blue-100 rounded hover:bg-blue-200 transition-colors'
          >
            <ComputerDesktopIcon className='h-3 w-3 mr-1' />
            Open in Tab
          </a>
        </div>
      </div>
    </div>
  )
}

export default CredentialsBar 