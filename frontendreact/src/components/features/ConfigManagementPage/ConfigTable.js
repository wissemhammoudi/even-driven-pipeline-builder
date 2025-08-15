import React from 'react'
import {
  EyeIcon,
  ExclamationTriangleIcon,
  CogIcon
} from '@heroicons/react/24/outline'
import Button from '../../common/Button/Button'

const ConfigTable = ({
  configs,
  title,
  isDeprecated = false,
  onViewConfig,
  onDeprecateConfig
}) => {
  if (configs.length === 0) {
    return (
      <div className='text-center py-8'>
        <CogIcon className='mx-auto h-12 w-12 text-gray-400' />
        <h3 className='mt-2 text-sm font-medium text-gray-900'>
          No {isDeprecated ? 'deprecated' : 'active'} configurations found
        </h3>
      </div>
    )
  }

  return (
    <div className='space-y-4'>
      {title && <h3 className='text-lg font-medium text-gray-900'>{title}</h3>}

      <div className='bg-white shadow overflow-hidden sm:rounded-md'>
        <div className='px-4 py-5 sm:p-6'>
          <div className='grid grid-cols-3 gap-4 border-b border-gray-200 pb-3'>
            <div className='font-medium text-gray-900'>Plugin Name</div>
            <div className='font-medium text-gray-900'>Plugin Type</div>
            <div className='font-medium text-gray-900'>Actions</div>
          </div>

          {configs.map(config => (
            <div
              key={config.step_config_id}
              className='grid grid-cols-3 gap-4 py-4 border-b border-gray-100 last:border-b-0'
            >
              <div className='text-sm text-gray-900'>{config.plugin_name}</div>
              <div className='text-sm text-gray-500'>{config.plugin_type}</div>
              <div className='flex items-center space-x-2'>
                <Button
                  onClick={() => onViewConfig(config)}
                  variant='secondary'
                  size='xs'
                  icon={EyeIcon}
                  iconPosition='left'
                  className='px-2 py-1 text-xs'
                >
                  View Config
                </Button>
                {!isDeprecated && (
                  <Button
                    onClick={() => onDeprecateConfig(config.step_config_id)}
                    variant='secondary'
                    size='xs'
                    icon={ExclamationTriangleIcon}
                    iconPosition='left'
                    className='px-2 py-1 text-xs text-red-700 bg-red-100 hover:bg-red-200 border-none'
                  >
                    Deprecate
                  </Button>
                )}
                {isDeprecated && (
                  <span className='inline-flex items-center px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-800'>
                    Deprecated
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default ConfigTable
