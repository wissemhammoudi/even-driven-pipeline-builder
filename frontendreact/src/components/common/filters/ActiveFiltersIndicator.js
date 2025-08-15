import React from 'react'

const ActiveFiltersIndicator = ({ filters = [], className = '' }) => {
  if (!filters.length) return null

  return (
    <div className={`mt-6 pt-4 border-t border-gray-200 ${className}`}>
      <div className='flex items-center space-x-2 text-sm text-gray-600'>
        <span className='font-medium'>Active filters:</span>
        {filters.map((filter, idx) => (
          <span
            key={idx}
            className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${filter.colorClass}`}
          >
            {filter.label}: {typeof filter.value === 'object' ? JSON.stringify(filter.value) : String(filter.value)}
          </span>
        ))}
      </div>
    </div>
  )
}

export default ActiveFiltersIndicator 