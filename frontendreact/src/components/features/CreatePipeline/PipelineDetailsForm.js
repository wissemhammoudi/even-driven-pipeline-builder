import React from 'react'
import Input from '../../common/Input/Input'

const PipelineDetailsForm = ({ formData, onInputChange }) => {
  return (
    <div className='bg-white shadow rounded-lg p-6'>
      <h2 className='text-lg font-medium text-gray-900 mb-4'>
        Pipeline Details
      </h2>
      <div className='grid grid-cols-1 gap-6'>
        <div>
          <Input
            label='Pipeline Name *'
            type='text'
            id='name'
            name='name'
            value={formData.name}
            onChange={onInputChange}
            placeholder='Enter a descriptive name for your pipeline (e.g., Customer Data ETL Pipeline)'
            maxLength={100}
            required
          />
          <p className='mt-1 text-xs text-gray-500'>
            {formData.name.length}/100 characters
          </p>
        </div>
        <div>
          <Input
            label='Description'
            as='textarea'
            id='description'
            name='description'
            rows={4}
            value={formData.description}
            onChange={onInputChange}
            placeholder='Describe the purpose and scope of your pipeline (e.g., Extracts customer data from CRM, transforms it for analytics, and loads into data warehouse)'
            maxLength={500}
            className='resize-none'
          />
          <p className='mt-1 text-xs text-gray-500'>
            {formData.description.length}/500 characters
          </p>
        </div>
      </div>
    </div>
  )
}

export default PipelineDetailsForm
