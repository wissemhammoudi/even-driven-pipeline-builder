import React from 'react'
import {
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon
} from '@heroicons/react/24/outline'
import StatCard from '../../../common/Card/StatsCard'

const PipelineStatsGrid = ({ stats }) => {
  const formatDuration = minutes => {
    if (minutes < 1) return '< 1 min'
    if (minutes < 60) return `${Math.round(minutes)} min`
    const hours = Math.floor(minutes / 60)
    const remainingMinutes = Math.round(minutes % 60)
    return `${hours}h ${remainingMinutes}m`
  }

  const formatDetailedDuration = stats => {
    if (!stats) return 'N/A'

    if (stats.avg_duration_formatted) {
      return stats.avg_duration_formatted
    }

    if (stats.avg_duration_minutes) {
      return formatDuration(stats.avg_duration_minutes)
    }

    return 'N/A'
  }

  return (
    <div className='mb-6'>
      <h2 className='text-xl font-semibold text-gray-800 mb-4'>
        Pipeline Performance Overview
      </h2>
      
              <div className='grid grid-cols-1 md:grid-cols-3 gap-6'>
          <StatCard 
            icon={CheckCircleIcon}
            title="Successful Runs"
            value={stats?.successful_runs || 0}
            color="green"
          />
          
          <StatCard 
            icon={XCircleIcon}
            title="Failed Runs"
            value={stats?.failed_runs || 0}
            color="red"
          />
          
          <StatCard 
            icon={ClockIcon}
            title="Avg Duration"
            value={formatDetailedDuration(stats)}
            color="primary"
          />
        </div>
    </div>
  )
}

export default PipelineStatsGrid 