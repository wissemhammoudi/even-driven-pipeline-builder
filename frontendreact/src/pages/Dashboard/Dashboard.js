import React, { useEffect, useCallback, useMemo } from 'react'
import useAuthStore from '../../store/authStore'
import useDashboardStore from '../../store/dashboardStore'
import PageHeader from '../../components/common/PageHeader'
import Button from '../../components/common/Button/Button'
import { PlusIcon, ArrowPathIcon } from '@heroicons/react/24/outline'
import { useNavigate } from 'react-router-dom'
import StatsGrid from '../../components/features/Dashboard/StatsGrid'
import MetricsGrid from '../../components/features/Dashboard/MetricsGrid'
import AnalyticsCharts from '../../components/features/Dashboard/AnalyticsCharts'
import RecentPipelines from '../../components/features/Dashboard/RecentPipelines'

const Dashboard = () => {
  const { user } = useAuthStore()
  const { 
    dashboardData, 
    isLoading, 
    isRefreshing, 
    error,
    loadDashboardData,
    refreshData,
    clearError
  } = useDashboardStore()

  const navigate = useNavigate()

  useEffect(() => {
    if (user?.user_id) {
      loadDashboardData(user.user_id)
    }
  }, [user?.user_id, loadDashboardData])

  const {
    stats: dashboardStats = {},
    charts: chartsData = {},
    recent_pipelines: recentPipelines = []
  } = useMemo(() => dashboardData || {}, [dashboardData])

  const handleRefresh = useCallback(() => {
    if (user?.user_id) {
      refreshData(user.user_id)
    }
  }, [user?.user_id, refreshData])

  const actions = useMemo(() => [
    <Button
      key='refresh'
      onClick={handleRefresh}
      disabled={isLoading || isRefreshing}
      className='inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-white bg-gray-600 hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50'
      icon={ArrowPathIcon}
      iconPosition='left'
    >
      {isRefreshing ? 'Refreshing...' : 'Refresh'}
    </Button>,
    user && user.role === 'admin' && (
      <Button
        key='create'
        onClick={() => navigate('/create-pipeline')}
        className='inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary hover:bg-primary-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500'
        icon={PlusIcon}
        iconPosition='left'
      >
        Create Pipeline
      </Button>
    )
  ], [handleRefresh, isLoading, isRefreshing, user, navigate])

  if (error) {
    return (
      <div className='space-y-6'>
        <PageHeader
          title='Dashboard'
          subtitle={`Welcome back, ${user?.username || 'User'}!`}
          actions={actions}
        />
        <div className='bg-red-50 border border-red-200 rounded-lg p-6'>
          <h3 className='text-lg font-medium text-red-800'>
            Error Loading Dashboard
          </h3>
          <p className='text-red-600 mt-2'>{error}</p>
          <div className='mt-4 space-x-2'>
            <Button
              onClick={handleRefresh}
              className='px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700'
            >
              Retry
            </Button>
            <Button
              onClick={clearError}
              className='px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400'
            >
              Dismiss
            </Button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className='space-y-6 relative'>
      <PageHeader
        title='Dashboard'
        subtitle={`Welcome back, ${user?.username || 'User'}!`}
        actions={actions}
      />

      {(isLoading || isRefreshing) && (
        <div className='absolute inset-0 z-50 flex flex-col items-center justify-center bg-white bg-opacity-80'>
          <div className='animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500 mb-4'></div>
          <span className='text-primary-700 font-medium text-lg'>Refreshing data...</span>
        </div>
      )}

      <StatsGrid dashboardStats={dashboardStats} />
      <MetricsGrid dashboardStats={dashboardStats} />
      <div className='bg-white shadow rounded-lg border border-primary-100'>
        <div className='px-4 py-5 sm:p-6'>
          {!isLoading && !isRefreshing && (
            <AnalyticsCharts
              pipelines={recentPipelines}
              chartsData={chartsData}
              userId={user?.user_id}
            />
          )}
        </div>
      </div>
      <RecentPipelines pipelines={recentPipelines} isLoading={isLoading} />
    </div>
  )
}

export default Dashboard