import React from 'react'
import { CheckIcon } from '@heroicons/react/24/outline'

const StepIndicator = ({ totalSteps, currentStep }) => (
  <div className='flex items-center justify-center mb-8'>
    {Array.from({ length: totalSteps }, (_, index) => (
      <div key={index} className='flex items-center'>
        <div
          className={`flex items-center justify-center w-8 h-8 rounded-full border-2 ${
            index + 1 === currentStep
              ? 'bg-primary border-primary text-white'
              : index + 1 < currentStep
              ? 'bg-green-500 border-green-500 text-white'
              : 'bg-gray-100 border-gray-300 text-gray-500'
          }`}
        >
          {index + 1 < currentStep ? (
            <CheckIcon className='w-5 h-5' />
          ) : (
            <span className='text-sm font-medium'>{index + 1}</span>
          )}
        </div>
        {index < totalSteps - 1 && (
          <div
            className={`w-16 h-0.5 mx-2 ${
              index + 1 < currentStep ? 'bg-green-500' : 'bg-gray-300'
            }`}
          />
        )}
      </div>
    ))}
  </div>
)

export default StepIndicator
