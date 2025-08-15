import React, { useState, useEffect, useRef, useMemo, useCallback } from 'react'
import { ConfigHeader, WarningState } from '../shared/utils'

const ColumnTransformationTab = ({
  availableTables = [],
  tableConfig = {},
  functionMapping = {},
  transformationSchema = {},
  columnFunctions = {},
  onColumnFunctionChange,
  updateTableSyncConfig,
  hasIngestionStep,
  ingestionStep
}) => {
  // Stable references to prevent unnecessary re-renders
  const safeAvailableTables = useMemo(() => Array.isArray(availableTables) ? availableTables : [], [availableTables])
  const safeTableConfig = useMemo(() => tableConfig || {}, [tableConfig])
  const safeFunctionMapping = useMemo(() => functionMapping || {}, [functionMapping])
  const safeTransformationSchema = useMemo(() => transformationSchema || {}, [transformationSchema])
  const safeColumnFunctions = useMemo(() => columnFunctions?.tables || columnFunctions || {}, [columnFunctions])

  const [selectedTable, setSelectedTable] = useState('')
  const selectedTableRef = useRef('')
  const initializedRef = useRef(false)

  useEffect(() => {
    if (safeAvailableTables.length > 0 && !selectedTable && !initializedRef.current) {
      const firstTable = safeAvailableTables[0].name
      setSelectedTable(firstTable)
      selectedTableRef.current = firstTable
      initializedRef.current = true
    }
  }, [safeAvailableTables, selectedTable])

  useEffect(() => {
    if (selectedTable) {
      selectedTableRef.current = selectedTable
    }
  }, [selectedTable])

  useEffect(() => {
    if (!selectedTable && selectedTableRef.current && safeAvailableTables.find(t => t.name === selectedTableRef.current)) {
      setSelectedTable(selectedTableRef.current)
    }
  }, [selectedTable, safeAvailableTables])

  useEffect(() => {
    if (initializedRef.current && safeAvailableTables.length > 0 && Object.keys(safeTableConfig).length > 0) {
      safeAvailableTables.forEach(table => {
        const tableColumns = safeTableConfig[table.name]
        if (tableColumns && Array.isArray(tableColumns)) {
          tableColumns.forEach(column => {
            const columnName = column.column_name || column.name
            if (columnName && !safeColumnFunctions[table.name]?.[columnName]) {
              onColumnFunctionChange(table.name, columnName, 'None')
            }
          })
        }
      })
    }
  }, [safeAvailableTables, safeTableConfig, safeColumnFunctions, onColumnFunctionChange])

  useEffect(() => {
    if (updateTableSyncConfig && Object.keys(safeTableConfig).length > 0) {
      updateTableSyncConfig()
    }
  }, [updateTableSyncConfig, safeTableConfig])

  const getOperationType = useCallback((functionName) => {
    // Create a reverse mapping from the dynamic transformationSchema
    const functionToOperationMap = {}
    
    // Build the reverse mapping from the transformation configuration
    Object.entries(safeTransformationSchema).forEach(([operationType, functions]) => {
      if (typeof functions === 'object' && functions !== null) {
        Object.keys(functions).forEach(funcName => {
          functionToOperationMap[funcName] = operationType
        })
      }
    })
    

    return functionToOperationMap[functionName] || 'null_value'
  }, [safeTransformationSchema])

  const formatFunctionForBackend = useCallback((functionName) => {
    if (!functionName || functionName === 'None') return 'None'
    const operationType = getOperationType(functionName)
    return `${operationType}:${functionName}`
  }, [getOperationType])

  const extractFunctionFromBackend = useCallback((backendValue) => {
    if (!backendValue || backendValue === 'None') return 'None'
    const parts = backendValue.split(':')
    return parts.length > 1 ? parts[1] : backendValue
  }, [])

  const handleTableChange = useCallback((tableName) => {
    setSelectedTable(tableName)
  }, [])

  const handleFunctionChange = useCallback((tableName, columnName, functionName) => {
    if (functionName && functionName !== '') {
      const formattedFunction = formatFunctionForBackend(functionName)
      onColumnFunctionChange(tableName, columnName, formattedFunction)
    } else {
      onColumnFunctionChange(tableName, columnName, 'None')
    }
  }, [formatFunctionForBackend, onColumnFunctionChange])
  
  if (safeAvailableTables.length === 0) {
    return (
      <WarningState 
        title="No Tables Available"
        message="No tables available for column transformations. Configure the source database in either the ingestion step or transformation step destination configuration."
      />
    )
  }

  return (
    <div className='space-y-4'>
      <ConfigHeader 
        color="blue"
        title="Column Transformations"
        message="Apply functions to transform your data columns"
      >
        <div className='mt-2 text-xs text-blue-600'>
          <p><strong>Available Tables:</strong> {safeAvailableTables.length} tables found</p>
          {safeAvailableTables.length > 0 && (
            <p><strong>Tables:</strong> {safeAvailableTables.map(t => t.name).join(', ')}</p>
          )}
          {hasIngestionStep && (
            <div>
              <p>Ingestion step found with configuration.</p>
              <p>Available config keys: {Object.keys(ingestionStep.step_config || {}).join(', ')}</p>
            </div>
          )}
        </div>
      </ConfigHeader>

      <div className='bg-white border border-gray-200 rounded-lg p-4'>
        <div className='mb-4'>
          <label className='block text-sm font-medium text-gray-700 mb-2'>
            Select Table
          </label>
          <select
            value={selectedTable}
            onChange={e => handleTableChange(e.target.value)}
            className='block w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary focus:border-primary'
          >
            <option value=''>Choose a table...</option>
            {safeAvailableTables.map(table => (
              <option key={table.name} value={table.name}>
                {table.name} ({Array.isArray(table.columns) ? table.columns.length : 0} columns)
              </option>
            ))}
          </select>
        </div>

        {selectedTable && !safeTableConfig[selectedTable] && (
          <div className='bg-yellow-50 border border-yellow-200 rounded-lg p-4'>
            <h6 className='font-medium text-yellow-900 mb-2'>
              Table Configuration Not Found
            </h6>
            <p className='text-sm text-yellow-700'>
              No column configuration found for table "{selectedTable}". 
              Available table configs: {Object.keys(safeTableConfig).join(', ')}
            </p>
          </div>
        )}

        {selectedTable && safeTableConfig[selectedTable] && (
          <div className='space-y-4'>
            <h6 className='font-medium text-gray-900'>
              Configure Column Functions for {selectedTable}
            </h6>
            
            <div className='text-xs text-gray-600 mb-2'>
              <p><strong>Table config found:</strong> {selectedTable}</p>
              <p><strong>Columns:</strong> {Array.isArray(safeTableConfig[selectedTable]) ? safeTableConfig[selectedTable].length : 0} columns</p>
              <p><strong>Column names:</strong> {Array.isArray(safeTableConfig[selectedTable]) ? safeTableConfig[selectedTable].map(c => c.column_name || c.name || 'unnamed').join(', ') : 'No columns found'}</p>
              <p><strong>Function mapping keys:</strong> {Object.keys(safeFunctionMapping).join(', ')}</p>
              <p><strong>Sample column data type:</strong> {safeTableConfig[selectedTable]?.[0]?.data_type || 'none'}</p>
            </div>
              
            <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4'>
              {Array.isArray(safeTableConfig[selectedTable]) && safeTableConfig[selectedTable].map((column, index) => {
                const dataType = (column.data_type || column.type || 'unknown').toLowerCase().trim();
                const mapping = {};
                Object.keys(safeFunctionMapping).forEach(key => {
                  mapping[key.toLowerCase().trim()] = safeFunctionMapping[key];
                });
                const functions = mapping[dataType] || [];
        
                const currentBackendValue = safeColumnFunctions[selectedTable]?.[column.column_name || column.name];
                const currentFunction = extractFunctionFromBackend(currentBackendValue);
                const valueToUse = functions.includes(currentFunction) ? currentFunction : '';
                
                return (
                  <div key={column.column_name || column.name || index} className='border border-gray-200 rounded-lg p-3'>
                    <div className='mb-2'>
                      <label className='block text-sm font-medium text-gray-700'>
                        {column.column_name || column.name || `Column ${index}`}
                      </label>
                      <span className='text-xs text-gray-500'>({column.data_type || column.type || 'unknown'})</span>
                    </div>
                    <select
                      value={valueToUse}
                      onChange={e => handleFunctionChange(selectedTable, column.column_name || column.name, e.target.value)}
                      className='block w-full px-2 py-1 text-sm border border-gray-300 rounded focus:ring-1 focus:ring-primary focus:border-primary'
                    >
                      <option value=''>No transformation</option>
                      {functions.map(func => (
                        <option key={func} value={func}>
                          {func}
                        </option>
                      ))}
                    </select>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default ColumnTransformationTab  