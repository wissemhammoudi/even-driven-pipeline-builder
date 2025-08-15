import React from 'react'
import { ArchiveBoxIcon } from '@heroicons/react/24/outline'

const TypeFilter = ({
  label = 'Type',
  activeLabel = 'Active',
  inactiveLabel = 'Deprecated',
  icon: Icon = ArchiveBoxIcon,
  isActive = true,
  onToggle,
  className = ''
}) => {
  return (
    <div className={`lg:col-span-3 ${className}`}>
      <label className='block text-sm font-semibold text-gray-700 mb-2'>
        {label}
      </label>
      <button
        onClick={() => onToggle && onToggle(!isActive)}
        className={`w-full flex items-center justify-center px-4 py-3 border-2 rounded-lg text-sm font-semibold transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 ${
          !isActive
            ? 'border-amber-300 bg-amber-50 text-amber-800 hover:bg-amber-100 focus:ring-amber-500'
            : 'border-emerald-300 bg-emerald-50 text-emerald-800 hover:bg-emerald-100 focus:ring-emerald-500'
        }`}
      >
        {Icon && <Icon className='h-5 w-5 mr-2' />}
        {!isActive ? inactiveLabel : activeLabel}
      </button>
    </div>
  )
}

export default TypeFilter 