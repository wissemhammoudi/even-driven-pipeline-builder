import React from 'react'
import { PlusIcon, ShieldExclamationIcon } from '@heroicons/react/24/outline'
import PipelineFilters from '../../components/features/PipelineManagement/PipelineFilters'
import PipelineTable from '../../components/features/PipelineManagement/PipelineTable'
import Pagination from '../../components/common/Pagination/Pagination'
import EmptyState from '../../components/features/PipelineManagement/EmptyState'
import PageHeader from '../../components/common/PageHeader'
import usePipelineManagementPage from './usePipelineManagementPage'

const PipelineManagementPage = () => {
  const {
    searchTerm,
    setSearchTerm,
    dateFilter,
    setDateFilter,
    showDeprecated,
    setShowDeprecated,
    paginatedResult,
    isLoading,
    isAdmin,
    handleCreatePipeline,
    handleViewPipeline,
    handleDeletePipeline,
    handlePageChange,
    handleClearFilters,
    hasPermission,
    actionLoading,
    permissionsLoading
  } = usePipelineManagementPage()

  return (
    <div className='space-y-6'>
      <PageHeader
        title='Pipeline Management'
        subtitle='Manage and monitor your data pipelines'
        actions={
          isAdmin() ? (
            <button
              onClick={handleCreatePipeline}
              className='inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500'
            >
              <PlusIcon className='h-4 w-4 mr-2' />
              Create Pipeline
            </button>
          ) : (
            <div className='flex items-center space-x-2 px-3 py-2 bg-yellow-50 border border-yellow-200 rounded-md'>
              <ShieldExclamationIcon className='h-4 w-4 text-yellow-600' />
              <span className='text-sm text-yellow-800 font-medium'>
                Admin access required to create pipelines
              </span>
            </div>
          )
        }
      />
      <PipelineFilters
        searchTerm={searchTerm}
        setSearchTerm={setSearchTerm}
        dateFilter={dateFilter}
        setDateFilter={setDateFilter}
        showDeprecated={showDeprecated}
        setShowDeprecated={setShowDeprecated}
        onClearFilters={handleClearFilters}
      />
      <div className='bg-white shadow rounded-lg'>
        <div className='px-4 py-5 sm:p-6'>
          {isLoading ? (
            <div className='flex flex-col items-center justify-center py-12'>
              <div className='animate-spin rounded-full h-8 w-8 border-b-2 border-primary mb-4'></div>
              <p className='text-gray-500'>Loading pipelines...</p>
            </div>
          ) : paginatedResult.items.length === 0 ? (
            <EmptyState
              totalPipelines={paginatedResult.items.length}
              showDeprecated={showDeprecated}
              isAdmin={isAdmin}
              onCreatePipeline={handleCreatePipeline}
            />
          ) : (
            <div className='space-y-8'>
              <PipelineTable
                pipelines={paginatedResult.items}
                title={
                  showDeprecated ? 'Deprecated Pipelines' : 'Active Pipelines'
                }
                onView={handleViewPipeline}
                onDelete={handleDeletePipeline}
                hasPermission={hasPermission}
                actionLoading={actionLoading}
                permissionsLoading={permissionsLoading}
                isAdmin={isAdmin}
                isDeprecated={showDeprecated}
              />
              <Pagination
                currentPage={paginatedResult.pagination.currentPage}
                totalPages={paginatedResult.pagination.totalPages}
                pageSize={paginatedResult.pagination.pageSize}
                totalItems={paginatedResult.pagination.totalItems}
                onPageChange={handlePageChange}
              />
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default PipelineManagementPage
