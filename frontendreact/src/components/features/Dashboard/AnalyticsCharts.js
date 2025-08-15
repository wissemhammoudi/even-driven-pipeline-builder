import React, { useState, useEffect, useCallback, useMemo } from 'react'
import dashboardApi from '../../../api/dashboardApi'
import TimeRangeSelector from '../../common/Charts/TimeRangeSelector'
import DoughnutChart from '../../common/Charts/DoughnutChart'
import LineChart from '../../common/Charts/LineChart'
import { getTimeRangeDays, createChartData, createLineChartData } from '../../../utils/formatters'

const AnalyticsCharts = ({ pipelines, chartsData, userId }) => {
  const [selectedTimeRange, setSelectedTimeRange] = useState('30d')
  const [filteredData, setFilteredData] = useState({
    pipelines: [],
    charts: {
      pipeline_creation_trend: [],
      pipeline_status_distribution: [],
      success_failure_distribution: []
    }
  })
  const [isLoadingCharts, setIsLoadingCharts] = useState(false)

  useEffect(() => {
    if (chartsData) {
      setFilteredData(prev => ({
        ...prev,
        charts: chartsData
      }))
    }
  }, [chartsData])

  const fetchChartsData = useCallback(async (timeRange) => {
    try {
      setIsLoadingCharts(true)
      const days = getTimeRangeDays(timeRange)
      const apiChartsData = await dashboardApi.getChartsData(userId, days)
      setFilteredData(prev => ({
        ...prev,
        charts: {
          pipeline_creation_trend: apiChartsData.pipeline_creation_trend || [],
          pipeline_status_distribution: apiChartsData.pipeline_status_distribution || [],
          success_failure_distribution: apiChartsData.success_failure_distribution || []
        }
      }))
    } catch (error) {
      console.error('Error fetching charts data:', error)
    } finally {
      setIsLoadingCharts(false)
    }
  }, [userId])

  const handleTimeRangeChange = useCallback((newTimeRange) => {
    setSelectedTimeRange(newTimeRange)
    fetchChartsData(newTimeRange)
  }, [fetchChartsData])

  const getPipelineStatusData = useMemo(() => {
    return createChartData(
      filteredData.charts?.pipeline_status_distribution || [],
      'status',
      ['#05BAEE', '#D6007F']
    )
  }, [filteredData.charts?.pipeline_status_distribution])

  const getPipelineCreationData = useMemo(() => {
    return createLineChartData(
      filteredData.charts?.pipeline_creation_trend || [],
      'date',
      'pipelines_created',
      'Pipelines Created'
    )
  }, [filteredData.charts?.pipeline_creation_trend])

  const getSuccessFailureData = useMemo(() => {
    return createChartData(
      filteredData.charts?.success_failure_distribution || [],
      'status',
      ['#05BAEE', '#D6007F']
    )
  }, [filteredData.charts?.success_failure_distribution])

  return (
    <div className='space-y-6'>
      <TimeRangeSelector
        selectedRange={selectedTimeRange}
        onRangeChange={handleTimeRangeChange}
        isLoading={isLoadingCharts}
      />

      {isLoadingCharts ? (
        <div className='flex justify-center py-8'>
          <div className='animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500'></div>
        </div>
      ) : (
        <div className='grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6'>
          <DoughnutChart
            title='Pipeline Status Distribution'
            data={getPipelineStatusData}
            colors={['#05BAEE', '#D6007F']}
            emptyMessage='No pipeline data available'
          />
          <LineChart
            title='Pipeline Creation Trend'
            data={getPipelineCreationData}
            options={{
              plugins: { legend: { display: false } },
              scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } } }
            }}
          />
          <DoughnutChart
            title='Success/Failure Distribution'
            data={getSuccessFailureData}
            colors={['#05BAEE', '#D6007F']}
            emptyMessage='No run data available'
          />
        </div>
      )}
    </div>
  )
}

export default AnalyticsCharts
