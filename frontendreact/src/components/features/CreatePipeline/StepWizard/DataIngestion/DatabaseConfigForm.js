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
  const [testingConnection, setTestingConnection] = useState(false)
  const databaseOptions = [
    { label: 'PostgreSQL', value: 'postgresql+psycopg2' }
  ]

  const testConnection = async () => {
    const connectionData = {
      host: parsedFields.host || currentConfig.host || '',
      dbname: parsedFields.database || currentConfig.database || '',
      user: parsedFields.user || currentConfig.user || '',
      password: parsedFields.password || currentConfig.password || '',
      port: parseInt(parsedFields.port || currentConfig.port || '5432'),
      schema: parsedFields.schema || currentConfig.schema || 'public'
    }

    if (!connectionData.host || !connectionData.dbname || !connectionData.user || !connectionData.password) {
      toast.error('Please fill in all required connection fields (host, database, username, password)')
      return
    }

    setTestingConnection(true)
    try {
      const result = await pipelineAPI.testConnection(connectionData)
      
      if (result.test_result?.status === 'success') {
        toast.success('Connection successful! Database is accessible.')
      } else {
        toast.error(`Connection failed: ${result.test_result?.error_message || 'Unknown error'}`)
      }
    } catch (error) {
      toast.error(`Connection test failed: ${error.message || 'Unknown error'}`)
    } finally {
      setTestingConnection(false)
    }
  }

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

      {/* Test Connection Button */}
      <div className='flex justify-center'>
        <button
          type='button'
          onClick={testConnection}
          disabled={testingConnection}
          className={`px-6 py-3 rounded-lg font-medium transition-colors duration-200 ${
            testingConnection
              ? 'bg-gray-400 cursor-not-allowed text-white'
              : 'bg-blue-600 hover:bg-blue-700 text-white'
          }`}
        >
          {testingConnection ? (
            <div className='flex items-center space-x-2'>
              <div className='animate-spin rounded-full h-4 w-4 border-b-2 border-white'></div>
              <span>Testing Connection...</span>
            </div>
          ) : (
            'Test Connection'
          )}
        </button>
      </div>
    </div>
  )
}

export default DatabaseConfigForm 