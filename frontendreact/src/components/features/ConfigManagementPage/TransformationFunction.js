import React from 'react'

const TransformationFunction = ({ func }) => (
  <div
    className='bg-white border border-gray-100 rounded-md p-3 hover:bg-gray-50 transition-colors'
  >
    <div className='flex justify-between items-start mb-2'>
      <span className='text-sm font-medium text-gray-900 capitalize'>
        {func.name}
      </span>
      <span className='text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full font-mono'>
        {func.syntax}
      </span>
    </div>
    <p className='text-xs text-gray-600 mb-2'>
      {func.description}
    </p>
    <div className='flex flex-wrap gap-1'>
      {func.supported_types.slice(0, 3).map((type, typeIndex) => (
        <span
          key={typeIndex}
          className='text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded'
        >
          {type}
        </span>
      ))}
      {func.supported_types.length > 3 && (
        <span className='text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded'>
          +{func.supported_types.length - 3} more
        </span>
      )}
    </div>
  </div>
)

export default TransformationFunction 