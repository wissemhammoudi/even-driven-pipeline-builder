import React from 'react'
import {
  EyeIcon,
  EyeSlashIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline'
import ConfigTable from './ConfigTable'
import Pagination from '../../common/Pagination/Pagination'

const ConfigurationsSection = ({
  selectedTool,
  selectedType,
  loading,
  showDeprecated,
  onToggleDeprecated,
  activeConfigs,
  deprecatedConfigs,
  currentPage,
  pageSize,
  onPageChange,
  onViewConfig,
  onDeprecateConfig
}) => {
  if (!selectedTool || !selectedType) return null

  const paginatedActiveConfigs = activeConfigs.slice(
    (currentPage - 1) * pageSize,
    currentPage * pageSize
  )
  const totalPages = Math.ceil(activeConfigs.length / pageSize)

  return (
    <div className='bg-white shadow rounded-lg p-6'>
      <div className='flex justify-between items-center mb-4'>
        <h2 className='text-lg font-medium text-gray-900'>
          Configurations for{' '}
          <span className='text-primary font-semibold'>{selectedTool}</span> -{' '}
          <span className='text-primary font-semibold'>{selectedType}</span>
        </h2>

        <button
          onClick={onToggleDeprecated}
          className={`inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md transition-colors ${
            showDeprecated
              ? 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              : 'bg-blue-50 text-primary hover:bg-blue-100'
          }`}
        >
          {showDeprecated ? (
            <>
              <EyeSlashIcon className='h-4 w-4 mr-2' />
              Hide Deprecated
            </>
          ) : (
            <>
              <EyeIcon className='h-4 w-4 mr-2' />
              Show Deprecated{' '}
              {deprecatedConfigs.length > 0 && `(${deprecatedConfigs.length})`}
            </>
          )}
        </button>
      </div>

      {loading ? (
        <div className='flex justify-center py-8'>
          <div className='animate-spin rounded-full h-8 w-8 border-b-2 border-primary'></div>
        </div>
      ) : (
        <div className='space-y-6'>
          {showDeprecated ? (
            <ConfigTable
              configs={deprecatedConfigs}
              title='Deprecated Configurations'
              isDeprecated={true}
              onViewConfig={onViewConfig}
              onDeprecateConfig={onDeprecateConfig}
            />
          ) : (
            <>
              <ConfigTable
                configs={paginatedActiveConfigs}
                title='Active Configurations'
                onViewConfig={onViewConfig}
                onDeprecateConfig={onDeprecateConfig}
              />

              {totalPages > 1 && (
                <Pagination
                  currentPage={currentPage}
                  totalPages={totalPages}
                  totalItems={activeConfigs.length}
                  pageSize={pageSize}
                  onPageChange={onPageChange}
                />
              )}

              {deprecatedConfigs.length > 0 && (
                <div className='mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-md'>
                  <div className='flex items-center'>
                    <ExclamationTriangleIcon className='h-5 w-5 text-yellow-400 mr-2' />
                    <span className='text-sm text-yellow-800'>
                      There are {deprecatedConfigs.length} deprecated
                      configuration(s) available. Click "Show Deprecated" to
                      view them.
                    </span>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  )
}

export default ConfigurationsSection
