import React from 'react'

const defaultRanges = [
  { label: '7d', value: '7d' },
  { label: '30d', value: '30d' },
  { label: '90d', value: '90d' },
  { label: 'All Time', value: 'all' }
]

const TimeRangeSelector = ({
  label = 'Analytics Overview',
  ranges = defaultRanges,
  selectedRange,
  onRangeChange,
  isLoading = false,
  className = ''
}) => {
  return (
    <div className={`flex justify-between items-center ${className}`}>
      <h3 className='text-lg font-medium text-gray-900'>{label}</h3>
      <div className='flex space-x-2'>
        {ranges.map(range => (
          <button
            key={range.value}
            onClick={() => onRangeChange(range.value)}
            disabled={isLoading}
            className={`px-3 py-1 text-sm font-medium rounded-md transition-colors ${
              selectedRange === range.value
                ? 'bg-primary text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            } ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            {range.label}
          </button>
        ))}
      </div>
    </div>
  )
}

export default TimeRangeSelector
