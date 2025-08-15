import React from 'react'

const JoinStepIndicator = ({ step }) => (
  <div className='flex items-center mb-4'>
    <div className='flex space-x-2'>
      {[1, 2, 3].map(stepNumber => (
        <div
          key={stepNumber}
          className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
            step >= stepNumber ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-600'
          }`}
        >
          {stepNumber}
        </div>
      ))}
    </div>
    <div className='ml-4'>
      <span className='text-sm font-medium text-gray-900'>
        {step === 1 && 'Model Name & Primary Table'}
        {step === 2 && 'Select Target Tables'}
        {step === 3 && 'Configure Each Table'}
      </span>
    </div>
  </div>
)

export default JoinStepIndicator 