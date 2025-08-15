import React, { useState, useMemo } from 'react'
import PropTypes from 'prop-types'
import { ConfigHeader, LoadingSpinner } from '../shared/utils'
import { useTransformation } from '../../../../../hooks/useTransformation'
import { cleanSQLResponse } from './utils/sqlUtils'
import { extractErrorMessage } from '../../../../../utils/errorHandler'

const AgenticTransformationTab = ({
  sourceConfigDisplay,
  agenticTransformations,
  onAddAgenticTransformation,
  onRemoveAgenticTransformation
}) => {
  const [agenticIntent, setAgenticIntent] = useState('')
  const [modelName, setModelName] = useState('')
  const [generatedSQL, setGeneratedSQL] = useState('')
  const [editableSQL, setEditableSQL] = useState('')
  const [isGenerating, setIsGenerating] = useState(false)
  const [generationError, setGenerationError] = useState('')

  const {
    createTransformation,
    testTransformation,
    validateTransformation,
    isLoading: isTransformationLoading,
    error: transformationError
  } = useTransformation()

  const defaultModelName = useMemo(() => {
    if (!agenticIntent.trim()) return ''

    const words = agenticIntent
      .toLowerCase()
      .replace(/[^a-z0-9\s]/g, '')
      .split(/\s+/)
      .filter(word => word.length > 2)
      .slice(0, 4)

    return words.join('_') || 'agentic_transformation'
  }, [agenticIntent])

  const handleIntentChange = value => {
    setAgenticIntent(value)
    if (!modelName.trim()) {
      setModelName(defaultModelName)
    }
  }

  const handleGenerateTransformation = async () => {
    if (!agenticIntent.trim() || !sourceConfigDisplay) return

    setIsGenerating(true)
    setGenerationError('')

    try {
      if (!sourceConfigDisplay?.host) {
        throw new Error('Database host is required')
      }

      const transformationData = {
        transformation: agenticIntent,
        schema_name: sourceConfigDisplay.schema || 'public',
        db_host: sourceConfigDisplay.host,
        db_port: sourceConfigDisplay.port || 5432,
        db_name: sourceConfigDisplay.database || sourceConfigDisplay.dbname,
        db_user: sourceConfigDisplay.user || sourceConfigDisplay.username,
        db_password: sourceConfigDisplay.password
      }

      const response = await createTransformation(transformationData)

      if (response.success && response.data) {
        const rawSQL = extractSQLFromResponse(response.data)

        if (rawSQL) {
          const cleanedSQL = cleanSQLResponse(rawSQL)
          setEditableSQL(cleanedSQL)
          setGeneratedSQL(cleanedSQL)
        } else {
          setGenerationError('No SQL content found in the response')
        }
      } else {
        setGenerationError(
          response.error || 'Failed to generate transformation'
        )
      }
    } catch (error) {
      console.error('Error generating transformation:', error)
      setGenerationError(extractErrorMessage(error, 'Failed to generate transformation'))
    } finally {
      setIsGenerating(false)
    }
  }

  const extractSQLFromResponse = (responseData) => {
    if (!responseData) return null

    if (typeof responseData === 'string') {
      return responseData.trim()
    }

    if (typeof responseData === 'object') {
      const sqlContent = responseData.result || 
                        responseData.sql || 
                        responseData.data || 
                        responseData.content ||
                        responseData.query ||
                        responseData.transformation

      if (sqlContent) {
        return typeof sqlContent === 'string' ? sqlContent.trim() : String(sqlContent)
      }

      for (const key in responseData) {
        const value = responseData[key]
        if (typeof value === 'string' && value.toLowerCase().includes('select')) {
          return value.trim()
        }
      }

      try {
        const stringified = JSON.stringify(responseData)
        if (stringified && stringified !== '{}') {
          return stringified
        }
      } catch {
      }
    }

    return null
  }

  const handleConfirmTransformation = () => {
    if (!editableSQL.trim()) return

    onAddAgenticTransformation({
      intent: agenticIntent,
      result: editableSQL,
      model_name: modelName.trim() || defaultModelName
    })

    setAgenticIntent('')
    setModelName('')
    setGeneratedSQL('')
    setEditableSQL('')
  }

  return (
    <div className='space-y-4'>
      <ConfigHeader
        color='purple'
        title='AI-Powered Transformations'
        message='Describe what you want to achieve in natural language, and AI will generate the SQL for you.'
      />

      {sourceConfigDisplay && (
        <div className='bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4'>
          <h5 className='text-sm font-medium text-blue-900 mb-2'>
            Source Database Configuration
          </h5>
          <div className='text-sm text-blue-700'>
            <p>
              <strong>Host:</strong> {sourceConfigDisplay.host}
            </p>
            <p>
              <strong>Port:</strong> {sourceConfigDisplay.port || 5432}
            </p>
            <p>
              <strong>Database:</strong>{' '}
              {sourceConfigDisplay.database || sourceConfigDisplay.dbname}
            </p>
            <p>
              <strong>Schema:</strong> {sourceConfigDisplay.schema || 'public'}
            </p>
            <p>
              <strong>User:</strong>{' '}
              {sourceConfigDisplay.user || sourceConfigDisplay.username}
            </p>
          </div>
        </div>
      )}

      <div className='bg-white border border-gray-200 rounded-lg p-4'>
        <h6 className='font-medium text-gray-900 mb-3'>
          Generate New Transformation
        </h6>

        <div className='mb-4'>
          <label className='block text-sm font-medium text-gray-700 mb-2'>
            Describe what you want to do (your intent)
          </label>
          <textarea
            value={agenticIntent}
            onChange={e => handleIntentChange(e.target.value)}
            placeholder='e.g., Calculate the average temperature by location and create a summary table'
            className='w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            rows={3}
          />
        </div>

        <div className='mb-4'>
          <label className='block text-sm font-medium text-gray-700 mb-2'>
            Model Name
          </label>
          <input
            type='text'
            value={modelName}
            onChange={e => setModelName(e.target.value)}
            placeholder='e.g., avg_temperature_by_location'
            className='w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent'
          />
          <p className='text-xs text-gray-500 mt-1'>
            This will be the name of the generated model file. Use lowercase
            letters, numbers, and underscores only.
          </p>
        </div>

        <button
          onClick={handleGenerateTransformation}
          disabled={
            isGenerating || !agenticIntent.trim() || !sourceConfigDisplay
          }
          className='bg-pink-500 text-white px-4 py-2 rounded-md hover:bg-pink-600 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center'
        >
          {isGenerating ? (
            <>
              <LoadingSpinner className='mr-2' />
              Generating...
            </>
          ) : (
            'Generate Transformation'
          )}
        </button>

        {generationError && (
          <div className='mt-3 p-3 bg-red-50 border border-red-200 rounded-md'>
            <p className='text-sm text-red-700'>
              <strong>Error:</strong> {generationError}
            </p>
            <p className='text-xs text-red-600 mt-1'>
              Please check that the transformation agent service is running and
              try again.
            </p>
          </div>
        )}
      </div>

      {generatedSQL && (
        <div className='bg-white border border-gray-200 rounded-lg p-4'>
          <h6 className='font-medium text-gray-900 mb-3'>
            Edit and Confirm Transformation
          </h6>
          <div className='mb-4'>
            <label className='block text-sm font-medium text-gray-700 mb-2'>
              Generated SQL (you can edit this before confirming)
            </label>
            <textarea
              value={editableSQL}
              onChange={e => setEditableSQL(e.target.value)}
              className='w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm'
              rows={8}
            />
          </div>
          <button
            onClick={handleConfirmTransformation}
            className='bg-primary text-white px-4 py-2 rounded-md hover:bg-primary/90'
          >
            Confirm Agentic Transformation
          </button>
        </div>
      )}

      <div className='bg-white border border-gray-200 rounded-lg p-4'>
        <h6 className='font-medium text-gray-900 mb-3'>
          Configured Agentic Transformations
        </h6>

        {agenticTransformations.length === 0 ? (
          <div className='text-center py-8 text-gray-500'>
            <p>No agentic transformations configured yet.</p>
            <p className='text-sm'>Generate your first transformation above.</p>
          </div>
        ) : (
          <div className='space-y-4'>
            {agenticTransformations.map((transformation, index) => (
              <div
                key={index}
                className='border border-gray-200 rounded-lg p-4'
              >
                <div className='flex justify-between items-start mb-3'>
                  <div className='flex-1'>
                    <h4 className='font-medium text-gray-900 mb-2'>
                      Intent {index + 1}: {transformation.intent}
                    </h4>
                    {transformation.model_name && (
                      <p className='text-sm text-blue-600 mb-2'>
                        Model:{' '}
                        <span className='font-mono'>
                          {transformation.model_name}
                        </span>
                      </p>
                    )}
                    <div className='bg-gray-50 p-3 rounded-md'>
                      <pre className='text-sm text-gray-800 whitespace-pre-wrap font-mono'>
                        {transformation.result}
                      </pre>
                    </div>
                  </div>
                  <button
                    onClick={() => onRemoveAgenticTransformation(index)}
                    className='text-red-600 hover:text-red-800 ml-4'
                  >
                    Remove
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

AgenticTransformationTab.propTypes = {
  sourceConfigDisplay: PropTypes.shape({
    host: PropTypes.string.isRequired,
    port: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    database: PropTypes.string,
    dbname: PropTypes.string,
    schema: PropTypes.string,
    user: PropTypes.string,
    username: PropTypes.string,
    password: PropTypes.string
  }),
  agenticTransformations: PropTypes.arrayOf(
    PropTypes.shape({
      intent: PropTypes.string.isRequired,
      result: PropTypes.string.isRequired,
      model_name: PropTypes.string
    })
  ).isRequired,
  onAddAgenticTransformation: PropTypes.func.isRequired,
  onRemoveAgenticTransformation: PropTypes.func.isRequired
}

AgenticTransformationTab.defaultProps = {
  sourceConfigDisplay: null,
  agenticTransformations: []
}

export default AgenticTransformationTab
