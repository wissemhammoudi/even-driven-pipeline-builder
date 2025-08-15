import React from 'react'
import { ChevronLeftIcon, ChevronRightIcon } from '@heroicons/react/24/outline'

const StepWizardNavigation = ({
  currentStep,
  totalSteps,
  onPrev,
  onNext,
  onCancel,
  onSave,
  isEditing,
  canProceed
}) => (
  <div className='flex justify-between mt-8 pt-6 border-t border-gray-200'>
    <button
      onClick={onPrev}
      disabled={currentStep === 1}
      className='inline-flex items-center px-6 py-3 border border-gray-300 shadow-sm text-sm font-medium rounded-lg text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200'
    >
      <ChevronLeftIcon className='h-4 w-4 mr-2' />
      Previous
    </button>
    <div className='flex space-x-3'>
      <button
        onClick={onCancel}
        className='px-6 py-3 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary transition-colors duration-200'
      >
        Cancel
      </button>
      {currentStep < totalSteps ? (
        <button
          onClick={onNext}
          disabled={!canProceed}
          className='inline-flex items-center px-6 py-3 border border-transparent text-sm font-medium rounded-lg shadow-sm text-white bg-primary hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200'
        >
          Next
          <ChevronRightIcon className='h-4 w-4 ml-2' />
        </button>
      ) : (
        <button
          onClick={onSave}
          disabled={!canProceed}
          className='inline-flex items-center px-6 py-3 border border-transparent text-sm font-medium rounded-lg shadow-sm text-white bg-primary hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200'
        >
          {isEditing ? 'Update Step' : 'Create Step'}
        </button>
      )}
    </div>
  </div>
)

export default StepWizardNavigation
