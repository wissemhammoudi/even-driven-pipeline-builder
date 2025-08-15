import React from 'react'
import {
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon
} from '@heroicons/react/24/outline'
import StatCard from '../../common/Card/StatsCard'

const StatsGrid = ({ dashboardStats }) => {
  const { pipelines = {}, runs = {} } = dashboardStats || {}

  return (
    <div className='grid grid-cols-1 md:grid-cols-4 gap-6'>
      <StatCard
        title='Active Pipelines'
        value={pipelines.active || 0}
        icon={CheckCircleIcon}
        color='primary'
      />
      <StatCard
        title='Success Runs'
        value={runs.successful || 0}
        icon={CheckCircleIcon}
        color='green'
      />
      <StatCard
        title='Failed Runs'
        value={runs.failed || 0}
        icon={XCircleIcon}
        color='red'
      />
      <StatCard
        title='Total Pipelines'
        value={pipelines.total || 0}
        icon={ClockIcon}
        color='gray'
      />
    </div>
  )
}

export default StatsGrid
