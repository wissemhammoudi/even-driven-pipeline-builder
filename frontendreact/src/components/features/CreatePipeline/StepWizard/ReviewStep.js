import React from 'react'
import { StepTypeEnum } from './utils'
const ReviewStep = ({
  formData,
  selectedTables,
  tableColumns,
  plugins,
  selectedSourcePlugin,
  selectedDestinationPlugin,
  utilityType
}) => {
  const toolPlugins = plugins[formData.step_config.tool] || {}
  let sourceSection = null
  let destinationSection = null

  if (toolPlugins.extractors && toolPlugins.extractors.length > 0) {
    sourceSection = 'extractor'
  } else if (toolPlugins.sources && toolPlugins.sources.length > 0) {
    sourceSection = 'source'
  }

  if (toolPlugins.loaders && toolPlugins.loaders.length > 0) {
    destinationSection = 'loader'
  } else if (toolPlugins.destinations && toolPlugins.destinations.length > 0) {
    destinationSection = 'destination'
  }

  const sourceConfig = sourceSection
    ? formData.step_config.connection_config[sourceSection]
    : null
  const destinationConfig = destinationSection
    ? formData.step_config.connection_config[destinationSection]
    : null

  return (
    <div className='space-y-6'>
      <div className='bg-purple-50 border border-purple-200 rounded-lg p-4'>
        <h4 className='text-sm font-medium text-purple-900 mb-2'>
          Review Configuration
        </h4>
        <p className='text-sm text-purple-700'>
          Review your step configuration before creating
        </p>
      </div>

      <div className='space-y-4'>
        <div className='bg-white border border-gray-200 rounded-lg p-4'>
          <h5 className='font-medium text-gray-900 mb-2'>Basic Information</h5>
          <div className='text-sm text-gray-600 space-y-1'>
            <p>
              <strong>Name:</strong> {formData.name}
            </p>
            <p>
              <strong>Description:</strong>{' '}
              {formData.description || 'No description'}
            </p>
            <p>
              <strong>Type:</strong> {formData.type}
            </p>
            <p>
              <strong>Tool:</strong>{' '}
              {formData.step_config.tool || 'Not selected'}
            </p>
          </div>
        </div>

        {sourceConfig && (
          <div className='bg-white border border-gray-200 rounded-lg p-4'>
            <h5 className='font-medium text-gray-900 mb-2'>
              Source Configuration
            </h5>
            <div className='text-sm text-gray-600 space-y-1'>
              <p>
                <strong>Plugin:</strong>{' '}
                {selectedSourcePlugin || 'Not selected'}
              </p>
              <p>
                <strong>Host:</strong> {sourceConfig.host || 'Not configured'}
              </p>
              <p>
                <strong>Port:</strong> {sourceConfig.port || '5432'}
              </p>
              <p>
                <strong>Database:</strong>{' '}
                {sourceConfig.database || 'Not configured'}
              </p>
              <p>
                <strong>User:</strong> {sourceConfig.user || 'Not configured'}
              </p>
              <p>
                <strong>Schema:</strong> {sourceConfig.schema || 'public'}
              </p>
            </div>
          </div>
        )}

        {destinationConfig && (
          <div className='bg-white border border-gray-200 rounded-lg p-4'>
            <h5 className='font-medium text-gray-900 mb-2'>
              Destination Configuration
            </h5>
            <div className='text-sm text-gray-600 space-y-1'>
              <p>
                <strong>Plugin:</strong>{' '}
                {selectedDestinationPlugin || 'Not selected'}
              </p>
              <p>
                <strong>Host:</strong>{' '}
                {destinationConfig.host || 'Not configured'}
              </p>
              <p>
                <strong>Port:</strong> {destinationConfig.port || '5432'}
              </p>
              <p>
                <strong>Database:</strong>{' '}
                {destinationConfig.database || 'Not configured'}
              </p>
              <p>
                <strong>User:</strong>{' '}
                {destinationConfig.user || 'Not configured'}
              </p>
              <p>
                <strong>Schema:</strong> {destinationConfig.schema || 'public'}
              </p>
            </div>
          </div>
        )}

        {formData.type === StepTypeEnum.DATA_TRANSFORMATION && (
          <div className='bg-white border border-gray-200 rounded-lg p-4'>
            <h5 className='font-medium text-gray-900 mb-2'>
              Transformation Configuration
            </h5>
            <div className='text-sm text-gray-600 space-y-1'>
              <p>
                <strong>Utility Plugin:</strong> {utilityType || 'Not selected'}
              </p>
              <p>
                <strong>Tool:</strong>{' '}
                {formData.step_config.tool || 'Not selected'}
              </p>
              {formData.step_config.column_functions?.tables &&
                Object.keys(formData.step_config.column_functions.tables).length >
                  0 && (
                  <p>
                    <strong>Column Transformations:</strong>{' '}
                    {Object.keys(formData.step_config.column_functions.tables).length}{' '}
                    table(s) configured
                  </p>
                )}
              {formData.step_config.join_transformations &&
                formData.step_config.join_transformations.length > 0 && (
                  <p>
                    <strong>Join Transformations:</strong>{' '}
                    {formData.step_config.join_transformations.length} join(s)
                    configured
                  </p>
                )}
              {formData.step_config.agentic_transformations &&
                formData.step_config.agentic_transformations.length > 0 && (
                  <p>
                    <strong>Agentic Transformations:</strong>{' '}
                    {formData.step_config.agentic_transformations.length}{' '}
                    transformation(s) configured
                  </p>
                )}
            </div>
          </div>
        )}

        {formData.type === StepTypeEnum.DATA_TRANSFORMATION &&
          formData.step_config.destination_config &&
          Object.keys(formData.step_config.destination_config).length > 0 && (
            <div className='bg-white border border-gray-200 rounded-lg p-4'>
              <h5 className='font-medium text-gray-900 mb-2'>
                Destination Database Configuration
              </h5>
              <div className='text-sm text-gray-600 space-y-1'>
                <p>
                  <strong>Host:</strong>{' '}
                  {formData.step_config.destination_config.host ||
                    'Not configured'}
                </p>
                <p>
                  <strong>Port:</strong>{' '}
                  {formData.step_config.destination_config.port || '5432'}
                </p>
                <p>
                  <strong>Database:</strong>{' '}
                  {formData.step_config.destination_config.database ||
                    'Not configured'}
                </p>
                <p>
                  <strong>User:</strong>{' '}
                  {formData.step_config.destination_config.user ||
                    'Not configured'}
                </p>
                <p>
                  <strong>Schema:</strong>{' '}
                  {formData.step_config.destination_config.schema || 'public'}
                </p>
                <p>
                  <strong>Password:</strong>{' '}
                  {formData.step_config.destination_config.password
                    ? '••••••••'
                    : 'Not configured'}
                </p>
              </div>
            </div>
          )}

        {formData.type === StepTypeEnum.DATA_VISUALIZATION && (
          <div className='bg-white border border-gray-200 rounded-lg p-4'>
            <h5 className='font-medium text-gray-900 mb-2'>
              Visualization Configuration
            </h5>
            <div className='text-sm text-gray-600 space-y-1'>
              <p>
                <strong>Utility Plugin:</strong> {utilityType || 'Not selected'}
              </p>
              <p>
                <strong>Tool:</strong> Superset (auto-configured)
              </p>
              {formData.step_config.source_config && (
                <p>
                  <strong>Source Config:</strong> Using existing source
                  configuration
                </p>
              )}
            </div>
          </div>
        )}

        {formData.type === StepTypeEnum.DATA_VISUALIZATION &&
          formData.step_config.destination_config &&
          Object.keys(formData.step_config.destination_config).length > 0 && (
            <div className='bg-white border border-gray-200 rounded-lg p-4'>
              <h5 className='font-medium text-gray-900 mb-2'>
                Database Connection Configuration
              </h5>
              <div className='text-sm text-gray-600 space-y-1'>
                <p>
                  <strong>Host:</strong>{' '}
                  {formData.step_config.destination_config.host ||
                    'Not configured'}
                </p>
                <p>
                  <strong>Port:</strong>{' '}
                  {formData.step_config.destination_config.port || '5432'}
                </p>
                <p>
                  <strong>Database:</strong>{' '}
                  {formData.step_config.destination_config.database ||
                    'Not configured'}
                </p>
                <p>
                  <strong>User:</strong>{' '}
                  {formData.step_config.destination_config.user ||
                    'Not configured'}
                </p>
                <p>
                  <strong>Schema:</strong>{' '}
                  {formData.step_config.destination_config.schema || 'public'}
                </p>
                <p>
                  <strong>Password:</strong>{' '}
                  {formData.step_config.destination_config.password
                    ? '••••••••'
                    : 'Not configured'}
                </p>
                {formData.step_config.destination_config.sqlalchemy_uri && (
                  <p>
                    <strong>SQLAlchemy URI:</strong>{' '}
                    {formData.step_config.destination_config.sqlalchemy_uri.replace(
                      /\/\/.*@/,
                      '//***:***@'
                    )}
                  </p>
                )}
              </div>
            </div>
          )}

        {selectedTables.size > 0 && (
          <div className='bg-white border border-gray-200 rounded-lg p-4'>
            <h5 className='font-medium text-gray-900 mb-2'>Table Selection</h5>
            <div className='text-sm text-gray-600 space-y-1'>
              <p>
                <strong>Selected Tables:</strong> {selectedTables.size} table(s)
              </p>
              <div className='mt-2'>
                {Array.from(selectedTables).map(table => (
                  <div key={table} className='flex items-center space-x-2'>
                    <span className='text-blue-600'>•</span>
                    <span>{table}</span>
                    {tableColumns[table] && (
                      <span className='text-gray-500'>
                        (
                        {tableColumns[table].filter(col => col.selected).length}{' '}
                        columns selected)
                      </span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {selectedTables.size === 0 && formData.type === StepTypeEnum.DATA_INGESTION && (
          <div className='bg-yellow-50 border border-yellow-200 rounded-lg p-4'>
            <h5 className='font-medium text-yellow-900 mb-2'>
              Table Selection
            </h5>
            <p className='text-sm text-yellow-700'>
              No tables selected. Please go back and select at least one table.
            </p>
          </div>
        )}
      </div>
    </div>
  )
}

export default ReviewStep
