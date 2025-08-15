import React from 'react'
import { CheckCircleIcon, ClockIcon } from '@heroicons/react/24/outline'
import StatCard from '../../common/Card/StatsCard'
import { formatDuration } from '../../../utils/formatters'

const MetricsGrid = ({ dashboardStats }) => {
  const { runs = {} } = dashboardStats || {}

  return (
    <div className='grid grid-cols-1 md:grid-cols-2 gap-6'>
      <StatCard
        title='Success Rate'
        value={`${runs.success_rate || 0}%`}
        subtitle={`${runs.successful || 0} successful out of ${runs.total || 0} total runs`}
        icon={CheckCircleIcon}
        color='green'
        iconPosition='right'
      />
      <StatCard
        title='Average Run Duration'
        value={formatDuration(runs)}
        subtitle='Average time per pipeline run'
        icon={ClockIcon}
        color='primary'
        iconPosition='right'
      />
    </div>
  )
}

export default MetricsGrid
