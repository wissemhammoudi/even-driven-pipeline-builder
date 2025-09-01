import React, { useState } from 'react'
import { pipelineAPI } from '../../../../../api/pipelineApi'
import toast from 'react-hot-toast'

const DatabaseConfigForm = ({
  pluginType,
  currentConfig,
  onConfigChange,
  parsedFields,
  handleFieldChange
}) => {
  const databaseOptions = [
    { label: 'PostgreSQL', value: 'postgresql+psycopg2' }
  ]

  const renderField = (key, label, type = 'text', placeholder = '', options = null) => {
    const value = parsedFields[key] || currentConfig[key] || ''
    
    if (options) {
      return (
        <select
          value={value}
          onChange={e => handleFieldChange(key, e.target.value)}
          className='block w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-primary focus:border-primary focus:border-gray-300/0 sm:text-sm transition-colors duration-200'
        >
          <option value=''>{placeholder}</option>
          {options.map(option => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      )
    }

    return (
      <input
        type={type}
        value={value}
        onChange={e => handleFieldChange(key, e.target.value)}
        className='block w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-primary focus:border-primary focus:border-gray-300/0 sm:text-sm transition-colors duration-200 placeholder-gray-400'
        placeholder={placeholder}
      />
    )
  }

  return (
    <div className='space-y-6'>
      <div className='grid grid-cols-2 gap-6'>
        <div className='space-y-2'>
          <label className='block text-sm font-medium text-gray-700'>Host</label>
          {renderField('host', 'Host', 'text', 'Database host address')}
        </div>

        <div className='space-y-2'>
          <label className='block text-sm font-medium text-gray-700'>Port</label>
          {renderField('port', 'Port', 'number', '5432')}
        </div>

        <div className='space-y-2'>
          <label className='block text-sm font-medium text-gray-700'>Username</label>
          {renderField('user', 'Username', 'text', 'Database username')}
        </div>

        <div className='space-y-2'>
          <label className='block text-sm font-medium text-gray-700'>Password</label>
          {renderField('password', 'Password', 'password', 'Database password')}
        </div>

        <div className='space-y-2'>
          <label className='block text-sm font-medium text-gray-700'>Database Name</label>
          {renderField('database', 'Database Name', 'text', 'Database name')}
        </div>

        <div className='space-y-2'>
          <label className='block text-sm font-medium text-gray-700'>Schema</label>
          {renderField('schema', 'Schema', 'text', 'public')}
        </div>

        {pluginType === 'source' && (
          <div className='space-y-2'>
            <label className='block text-sm font-medium text-gray-700'>Database Type</label>
            {renderField('drivername', 'Database Type', 'select', 'Select a database type', databaseOptions)}
          </div>
        )}
      </div>
    </div>
  )
}

export default DatabaseConfigForm 