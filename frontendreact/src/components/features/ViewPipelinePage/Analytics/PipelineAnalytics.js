import React, { useState, useEffect, useCallback } from 'react'
import dashboardApi from '../../../../api/dashboardApi'
import toast from 'react-hot-toast'
import PipelineStatsGrid from './PipelineStatsGrid'
import PipelineChartsGrid from './PipelineChartsGrid'

const PipelineAnalytics = ({ pipelineId, days = 30, refreshTrigger = 0 }) => {
  const [analytics, setAnalytics] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const loadAnalytics = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await dashboardApi.getPipelineAnalytics(pipelineId, days)
      setAnalytics(data)
    } catch (err) {
      setError('Failed to load pipeline analytics')
      toast.error('Failed to load pipeline analytics')
    } finally {
      setLoading(false)
    }
  }, [pipelineId, days])

  useEffect(() => {
    if (pipelineId) {
      loadAnalytics()
    }
  }, [pipelineId, days, refreshTrigger, loadAnalytics])

  if (loading) {
    return (
      <div className='space-y-6'>
        {/* Simple Stats Loading */}
        <div className='grid grid-cols-1 md:grid-cols-3 gap-6'>
          <div className='bg-white shadow rounded-lg p-6 animate-pulse'>
            <div className='h-16 bg-gray-200 rounded'></div>
          </div>
          <div className='bg-white shadow rounded-lg p-6 animate-pulse'>
            <div className='h-16 bg-gray-200 rounded'></div>
          </div>
          <div className='bg-white shadow rounded-lg p-6 animate-pulse'>
            <div className='h-16 bg-gray-200 rounded'></div>
          </div>
        </div>

        {/* Simple Charts Loading */}
        <div className='grid grid-cols-1 lg:grid-cols-2 gap-6'>
          <div className='bg-white shadow rounded-lg p-6 animate-pulse'>
            <div className='h-80 bg-gray-200 rounded'></div>
          </div>
          <div className='bg-white shadow rounded-lg p-6 animate-pulse'>
            <div className='h-80 bg-gray-200 rounded'></div>
          </div>
        </div>
      </div>
    )
  }

  if (error || !analytics) {
    return (
      <div className='bg-white shadow rounded-lg p-6'>
        <div className='text-center py-8'>
          <h3 className='text-lg font-medium text-gray-900 mb-2'>
            Error Loading Analytics
          </h3>
          <p className='text-gray-500 mb-4'>
            {error || 'No analytics data available'}
          </p>
          <button
            onClick={loadAnalytics}
            className='inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 transition-colors'
          >
            Try Again
          </button>
        </div>
      </div>
    )
  }

  const { stats, charts } = analytics

  return (
    <div className='space-y-6'>
      <PipelineStatsGrid stats={stats} />
      <PipelineChartsGrid charts={charts} />
    </div>
  )
}

export default PipelineAnalytics 