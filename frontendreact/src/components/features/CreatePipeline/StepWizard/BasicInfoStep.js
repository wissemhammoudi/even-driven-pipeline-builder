import React from 'react'
import { StepTypeEnum } from './utils'
const BasicInfoStep = ({
  formData,
  toolsByType,
  stepTypes,
  existingVisualizationSteps,
  onInputChange,
  onToolChange
}) => {
  const isToolsLoading =
    !toolsByType[formData.type] || toolsByType[formData.type].length === 0
  const getAvailableStepTypes = () => {
    const types =
      stepTypes.length > 0
        ? stepTypes
        : [StepTypeEnum.DATA_INGESTION, StepTypeEnum.DATA_TRANSFORMATION, StepTypeEnum.DATA_VISUALIZATION]

    if (existingVisualizationSteps.length > 0) {
      return types.filter(type => type !== StepTypeEnum.DATA_VISUALIZATION)
    }

    return types
  }

  return (
    <div className='space-y-6'>
      <div>
        <label className='block text-sm font-semibold text-gray-700 mb-2'>
          Step Name *
        </label>
        <input
          type='text'
          value={formData.name}
          onChange={e => onInputChange('name', e.target.value)}
          className='block w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-primary focus:border-primary focus:border-gray-300/0 sm:text-sm transition-colors duration-200 placeholder-gray-400'
          placeholder='Enter a descriptive name for this step (e.g., Extract Customer Data)'
          maxLength={100}
          required
        />
        <p className='mt-1 text-xs text-gray-500'>
          {formData.name.length}/100 characters
        </p>
      </div>

      <div>
        <label className='block text-sm font-semibold text-gray-700 mb-2'>
          Description
        </label>
        <textarea
          value={formData.description}
          onChange={e => onInputChange('description', e.target.value)}
          rows={4}
          className='block w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-primary focus:border-primary focus:border-gray-300/0 sm:text-sm transition-colors duration-200 placeholder-gray-400 resize-none'
          placeholder='Describe what this step does (e.g., Extracts customer data from PostgreSQL database)'
          maxLength={500}
        />
        <p className='mt-1 text-xs text-gray-500'>
          {formData.description.length}/500 characters
        </p>
      </div>

      <div>
        <label className='block text-sm font-semibold text-gray-700 mb-2'>
          Step Type
        </label>
        <select
          value={formData.type}
          onChange={e => onInputChange('type', e.target.value)}
          className='block w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-primary focus:border-primary focus:border-gray-300/0 sm:text-sm transition-colors duration-200'
        >
          {getAvailableStepTypes().map(type => (
            <option key={type} value={type}>
              {type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label className='block text-sm font-semibold text-gray-700 mb-2'>
          Choose Tool *
        </label>
        <select
          value={formData.step_config.tool || ''}
          onChange={e => onToolChange(e.target.value)}
          disabled={isToolsLoading}
          className='block w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-primary focus:border-primary focus:border-gray-300/0 sm:text-sm transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed'
        >
          <option value=''>Select a tool</option>
          {isToolsLoading ? (
            <option value=''>Loading tools...</option>
          ) : (
            toolsByType[formData.type] &&
            toolsByType[formData.type].map(tool => (
              <option key={tool} value={tool}>
                {tool.charAt(0).toUpperCase() + tool.slice(1)}
              </option>
            ))
          )}
        </select>
        {isToolsLoading && (
          <p className='mt-1 text-xs text-gray-500'>
            Loading available tools...
          </p>
        )}
      </div>
    </div>
  )
}

export default BasicInfoStep
