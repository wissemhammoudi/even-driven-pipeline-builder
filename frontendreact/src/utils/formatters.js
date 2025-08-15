export const formatDuration = (runs) => {
  return (
    runs.avg_duration_formatted ||
    (runs.avg_duration_seconds
      ? `${runs.avg_duration_seconds.toFixed(3)}s`
      : `${runs.avg_duration_minutes || 0} min`)
  )
}

export const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString()
}

export const formatTimestamp = (timestamp) => {
  if (!timestamp) return 'N/A'
  return timestamp.replace('T', ' ').split('.')[0]
}

export const getTimeRangeDays = (timeRange) => {
  switch (timeRange) {
    case '7d':
      return 7
    case '30d':
      return 30
    case '90d':
      return 90
    case 'all':
      return 365
    default:
      return 30
  }
}

export const createChartData = (data, labels, colors = ['#05BAEE', '#D6007F']) => {
  if (!data || data.length === 0) {
    return {
      labels: [],
      datasets: [
        {
          data: [],
          backgroundColor: colors,
          borderWidth: 2
        }
      ]
    }
  }
  
  const chartLabels = data.map(item => item[labels])
  const chartData = data.map(item => item.count)
  
  return {
    labels: chartLabels,
    datasets: [
      {
        data: chartData,
        backgroundColor: colors,
        borderWidth: 2
      }
    ]
  }
}

export const createLineChartData = (data, labelKey, valueKey, label = 'Data') => {
  if (!data || data.length === 0) {
    return {
      labels: [],
      datasets: [
        {
          label,
          data: [],
          borderColor: '#05BAEE',
          backgroundColor: 'rgba(5, 186, 238, 0.1)',
          fill: true,
          tension: 0.4
        }
      ]
    }
  }
  
  const labels = data.map(item => item[labelKey])
  const values = data.map(item => item[valueKey])
  
  return {
    labels,
    datasets: [
      {
        label,
        data: values,
        borderColor: '#05BAEE',
        backgroundColor: 'rgba(5, 186, 238, 0.1)',
        fill: true,
        tension: 0.4
      }
    ]
  }
} 

export const calculateDuration = (startTime, endTime) => {
  if (!startTime || !endTime) return 'N/A'
  try {
    const start = new Date(startTime)
    const end = new Date(endTime)
    const duration = end - start
    const minutes = Math.floor(duration / 60000)
    const seconds = Math.floor((duration % 60000) / 1000)
    if (minutes > 0) {
      return `${minutes}m ${seconds}s`
    }
    return `${seconds}s`
  } catch (error) {
    return 'N/A'
  }
} 