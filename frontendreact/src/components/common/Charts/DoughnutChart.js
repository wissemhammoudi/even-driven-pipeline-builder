import React from 'react'
import {
  Chart as ChartJS,
  ArcElement,
  Title as ChartTitle,
  Tooltip,
  Legend
} from 'chart.js'
import { Doughnut } from 'react-chartjs-2'

ChartJS.register(
  ArcElement,
  ChartTitle,
  Tooltip,
  Legend
)

const DoughnutChart = ({
  title,
  data,
  colors = ['#05BAEE', '#EF4444', '#F59E0B', '#6B7280'],
  emptyMessage = 'No data available',
  className = ''
}) => {
  const hasData = data.labels && data.labels.length > 0

  const chartData = {
    labels: data.labels || [],
    datasets: [
      {
        data: data.datasets?.[0]?.data || [],
        backgroundColor: data.datasets?.[0]?.backgroundColor || colors,
        borderWidth: 2,
        borderColor: '#ffffff',
        hoverBorderWidth: 3
      }
    ]
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          padding: 20,
          usePointStyle: true,
          pointStyle: 'circle',
          font: {
            size: 12
          }
        }
      },
      tooltip: {
        callbacks: {
          label: (context) => {
            const total = context.dataset.data.reduce((a, b) => a + b, 0)
            const percentage = ((context.parsed / total) * 100).toFixed(1)
            return `${context.label}: ${context.parsed} (${percentage}%)`
          }
        }
      }
    },
    cutout: '60%'
  }

  if (!hasData) {
    return (
      <div className={`bg-white p-4 rounded-lg border ${className}`}>
        {title && <h4 className='text-md font-medium text-gray-900 mb-4'>{title}</h4>}
        <div className='h-64 flex items-center justify-center'>
          <p className='text-gray-500 text-sm'>{emptyMessage}</p>
        </div>
      </div>
    )
  }

  return (
    <div className={`bg-white p-4 rounded-lg border ${className}`}>
      {title && <h4 className='text-md font-medium text-gray-900 mb-4'>{title}</h4>}
      <div className='h-64'>
        <Doughnut data={chartData} options={options} />
      </div>
    </div>
  )
}

export default DoughnutChart 