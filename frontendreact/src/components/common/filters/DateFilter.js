import React from 'react'
import { CalendarDaysIcon, XMarkIcon } from '@heroicons/react/24/outline'

const DateFilter = ({ dateFilter, setDateFilter, label = 'Created Date', className = '' }) => {
  return (
    <div className={`lg:col-span-3 ${className}`}>
      <label htmlFor='dateFilter' className='block text-sm font-semibold text-gray-700 mb-2'>
        {label}
      </label>
      <div className='relative'>
        <div className='absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none'>
          <CalendarDaysIcon className='h-5 w-5 text-gray-400' />
        </div>
        <input
          type='date'
          id='dateFilter'
          value={dateFilter}
          onChange={(e) => setDateFilter(e.target.value)}
          className='block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200'
        />
        {dateFilter && (
          <button
            onClick={() => setDateFilter('')}
            className='absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600'
          >
            <XMarkIcon className='h-5 w-5' />
          </button>
        )}
      </div>
    </div>
  )
}

export default DateFilter 