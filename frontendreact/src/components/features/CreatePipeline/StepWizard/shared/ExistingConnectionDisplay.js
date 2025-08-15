import React from 'react'

const ExistingConnectionDisplay = ({ destinationConfig, useExistingConnection }) => {
  if (!useExistingConnection || !destinationConfig) {
    return null
  }

  return (
    <div className='mt-4 bg-green-50 border border-green-200 rounded-lg p-3'>
      <h6 className='text-sm font-medium text-green-900 mb-2'>
        Using Existing Configuration
      </h6>
      <div className='text-sm text-green-700 space-y-1'>
        <p>
          <strong>Source:</strong>{' '}
          {destinationConfig.source === 'transformation'
            ? 'Transformation Step'
            : 'Ingestion Step'}
        </p>
        <p>
          <strong>Host:</strong> {destinationConfig.host || 'Not configured'}
        </p>
        <p>
          <strong>Port:</strong> {destinationConfig.port || 5432}
        </p>
        <p>
          <strong>Database:</strong> {destinationConfig.database || 'Not configured'}
        </p>
        <p>
          <strong>User:</strong> {destinationConfig.user || 'Not configured'}
        </p>
        <p>
          <strong>Schema:</strong> {destinationConfig.schema || 'public'}
        </p>
        {destinationConfig.tool && (
          <p>
            <strong>{destinationConfig.source === 'transformation' ? 'Transformation' : 'Ingestion'} Tool:</strong>{' '}
            {destinationConfig.tool}
          </p>
        )}
      </div>
    </div>
  )
}

export default ExistingConnectionDisplay 