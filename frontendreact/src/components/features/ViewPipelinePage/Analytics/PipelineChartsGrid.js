import React from 'react'
import LineChart from '../../../common/Charts/LineChart'
import BarChart from '../../../common/Charts/BarChart'

const PipelineChartsGrid = ({ charts }) => {
  const formatDate = dateString => new Date(dateString).toLocaleDateString()

  const dailyRunsData = charts.daily_runs?.length ? {
    labels: charts.daily_runs.slice(-7).map(day => formatDate(day.date)),
    datasets: [
      {
        label: 'Successful',
        data: charts.daily_runs.slice(-7).map(day => day.successful_runs),
        borderColor: '#05BAEE',
        backgroundColor: 'rgba(5, 186, 238, 0.1)',
        tension: 0.4,
        fill: true
      },
      {
        label: 'Failed',
        data: charts.daily_runs.slice(-7).map(day => day.failed_runs),
        borderColor: '#D6007F',
        backgroundColor: 'rgba(214, 0, 127, 0.1)',
        tension: 0.4,
        fill: true
      }
    ]
  } : {
    labels: [],
    datasets: [
      {
        label: 'Successful',
        data: [],
        borderColor: '#05BAEE',
        backgroundColor: 'rgba(5, 186, 238, 0.1)',
        tension: 0.4,
        fill: true
      },
      {
        label: 'Failed',
        data: [],
        borderColor: '#D6007F',
        backgroundColor: 'rgba(214, 0, 127, 0.1)',
        tension: 0.4,
        fill: true
      }
    ]
  }

  const durationData = charts.duration_distribution?.length ? {
    labels: charts.duration_distribution.map(bucket => bucket.range),
    datasets: (() => {
      const datasets = []
      
      const hasSuccessfulRuns = charts.duration_distribution.some(bucket => bucket.success_count > 0)
      if (hasSuccessfulRuns) {
        datasets.push({
          label: 'Successful',
          data: charts.duration_distribution.map(bucket => bucket.success_count || 0),
          backgroundColor: 'rgba(5, 186, 238, 0.8)',
          borderRadius: 4
        })
      }
      
      const hasFailedRuns = charts.duration_distribution.some(bucket => bucket.failure_count > 0)
      if (hasFailedRuns) {
        datasets.push({
          label: 'Failed',
          data: charts.duration_distribution.map(bucket => bucket.failure_count || 0),
          backgroundColor: 'rgba(214, 0, 127, 0.8)',
          borderRadius: 4
        })
      }
      
      return datasets
    })()
  } : {
    labels: [],
    datasets: []
  }

  return (
    <div className='grid grid-cols-1 lg:grid-cols-2 gap-6'>
      <LineChart 
        data={dailyRunsData} 
        title="Daily Run Activity"
        className="shadow rounded-lg"
      />
      <BarChart 
        data={durationData} 
        title="Duration Distribution"
        className="shadow rounded-lg"
      />
    </div>
  )
}

export default PipelineChartsGrid 