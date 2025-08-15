import React from 'react'
import { CheckIcon } from '@heroicons/react/24/outline'

const SelectionCard = ({
  title,
  items,
  selectedItem,
  loading,
  onSelect,
  icon: Icon,
  emptyMessage = 'No items available'
}) => {
  if (loading) {
    return (
      <div className='bg-white shadow rounded-lg p-6'>
        <h2 className='text-lg font-medium text-gray-900 mb-4'>{title}</h2>
        <div className='flex justify-center py-4'>
          <div className='animate-spin rounded-full h-6 w-6 border-b-2 border-primary'></div>
        </div>
      </div>
    )
  }

  if (items.length === 0) {
    return (
      <div className='bg-white shadow rounded-lg p-6'>
        <h2 className='text-lg font-medium text-gray-900 mb-4'>{title}</h2>
        <div className='text-center py-8 text-gray-500'>{emptyMessage}</div>
      </div>
    )
  }

  return (
    <div className='bg-white shadow rounded-lg p-6'>
      <h2 className='text-lg font-medium text-gray-900 mb-4'>{title}</h2>
      <div className='grid grid-cols-1 md:grid-cols-3 gap-3'>
        {items.map(item => (
          <button
            key={item}
            onClick={() => onSelect(item)}
            className={`p-4 rounded-lg border-2 transition-colors ${
              selectedItem === item
                ? 'border-primary bg-blue-50 text-primary shadow-md'
                : 'border-gray-200 bg-white text-gray-700 hover:border-gray-300 hover:bg-gray-50'
            }`}
          >
            <div className='flex items-center justify-between w-full'>
              <div className='flex items-center'>
                {Icon && <Icon className='h-5 w-5 mr-2' />}
                <span className='font-medium'>{item}</span>
              </div>
              {selectedItem === item && (
                <CheckIcon className='h-5 w-5 text-primary' />
              )}
            </div>
          </button>
        ))}
      </div>
    </div>
  )
}

export default SelectionCard
