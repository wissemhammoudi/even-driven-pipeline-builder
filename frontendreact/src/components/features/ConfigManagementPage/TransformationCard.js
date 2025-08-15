import React from 'react'
import { getTransformationIcon } from './utils'
import TransformationFunction from './TransformationFunction'

const TransformationCard = ({ transformation }) => (
  <div
    className='border border-gray-200 rounded-lg p-6 hover:shadow-lg transition-all duration-200 bg-gradient-to-br from-gray-50 to-white'
  >
    <div className='flex items-center mb-4'>
      {getTransformationIcon(transformation.icon)}
      <div className='ml-3'>
        <h3 className='text-lg font-semibold text-gray-900'>
          {transformation.name}
        </h3>
        <p className='text-sm text-gray-600'>
          {transformation.description}
        </p>
      </div>
    </div>
    <div className='space-y-3'>
      <h4 className='text-sm font-medium text-gray-700 border-b border-gray-200 pb-2'>
        Available Functions ({transformation.functions.length})
      </h4>
      <div className='space-y-2'>
        {transformation.functions.map((func, funcIndex) => (
          <TransformationFunction key={funcIndex} func={func} />
        ))}
      </div>
    </div>
  </div>
)

export default TransformationCard 