import React from 'react'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title as ChartTitle,
  Tooltip,
  Legend
} from 'chart.js'
import { Bar } from 'react-chartjs-2'

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  ChartTitle,
  Tooltip,
  Legend
)

const BarChart = ({ data, title = 'Bar Chart', options = {}, className = '' }) => {
  const defaultOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom'
      }
    },
    scales: {
      y: {
        beginAtZero: true
      }
    },
    ...options
  }

  return (
    <div className={`bg-white p-4 rounded-lg border ${className}`}>
      {title && <h4 className='text-md font-medium text-gray-900 mb-4'>{title}</h4>}
      <div className='h-64'>
        <Bar data={data} options={defaultOptions} />
      </div>
    </div>
  )
}

export default BarChart 