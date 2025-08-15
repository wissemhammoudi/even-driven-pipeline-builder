import React, { useState, useEffect } from 'react'
import DatabaseConfigForm from './DatabaseConfigForm'

const DynamicConfigFields = ({
  pluginType,
  pluginSchema,
  currentConfig,
  onConfigChange
}) => {
  const [parsedFields, setParsedFields] = useState({})

  useEffect(() => {
    if (!pluginSchema || Object.keys(pluginSchema).length === 0) return

    setParsedFields(prev => {
      if (Object.keys(prev).length === 0) {
        const parsed = {
          user: currentConfig.user || currentConfig.username || '',
          password: currentConfig.password || '',
          host: currentConfig.host || '',
          port: currentConfig.port || '',
          database: currentConfig.database || currentConfig.dbname || '',
          schema: currentConfig.schema || currentConfig.default_target_schema || '',
          drivername: currentConfig.drivername || ''
        }
        return parsed
      }
      return prev
    })
  }, [pluginSchema])

  const handleFieldChange = (field, value) => {
    setParsedFields(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const handleConfigChange = (field, value) => {
    handleFieldChange(field, value)
    onConfigChange(pluginType, field, value)
  }

  if (!pluginSchema || Object.keys(pluginSchema).length === 0) {
    return (
      <div className='bg-yellow-50 border border-yellow-200 rounded-lg p-4'>
        <p className='text-sm text-yellow-700'>
          Please select a plugin above to load the connection configuration.
        </p>
      </div>
    )
  }

  return (
    <div className='space-y-4'>
      <DatabaseConfigForm
        pluginType={pluginType}
        currentConfig={currentConfig}
        onConfigChange={onConfigChange}
        parsedFields={parsedFields}
        handleFieldChange={handleConfigChange}
      />
    </div>
  )
}

export default DynamicConfigFields
