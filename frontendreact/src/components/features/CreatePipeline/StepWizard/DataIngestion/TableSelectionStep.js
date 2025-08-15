import React, { useEffect, useState, useCallback } from 'react'
import { ExclamationTriangleIcon } from '@heroicons/react/24/outline'
import { ErrorState, LoadingState, ConfigHeader } from '../shared/utils'
import { useDatabaseConnection } from '../shared/useDatabaseConnection'
import { useSchemaInfo } from '../shared/useSchemaInfo'

const TableSelectionStep = ({
  formData,
  selectedTables,
  tableColumns,
  searchTerm,
  expandedTables,
  setSelectedTables,
  setTableColumns,
  setSearchTerm,
  setExpandedTables,
  selectedSourcePlugin
}) => {
  const selectedTool = formData.step_config.tool

  const { connectionConfig, isLoadingConnection, connectionError } = useDatabaseConnection(
    formData,
    'ingestion'
  )

  const { 
    schemaInfo, 
    isLoadingSchema, 
    schemaError, 
    getAllTables, 
    getTableColumns
  } = useSchemaInfo(connectionConfig)

  const handleSelectAll = useCallback(checked => {
    const allTableNames = getAllTables().map(table => table.name)
    setSelectedTables(checked ? new Set(allTableNames) : new Set())
    
    if (checked) {
      const allTableColumns = {}
      allTableNames.forEach(tableName => {
        const columns = getTableColumns(tableName)
        allTableColumns[tableName] = columns.map(column => ({
          ...column,
          selected: true
        }))
      })
      setTableColumns(allTableColumns)
    } else {
      setTableColumns({})
    }
  }, [getAllTables, setSelectedTables, getTableColumns, setTableColumns])

  const handleTableToggle = useCallback(tableName => {
    setSelectedTables(prev => {
      const newSet = new Set(prev)
      if (newSet.has(tableName)) {
        newSet.delete(tableName)
        setTableColumns(prevCols => {
          const newCols = { ...prevCols }
          delete newCols[tableName]
          return newCols
        })
      } else {
        newSet.add(tableName)
        const columns = getTableColumns(tableName)
        const columnsWithSelection = columns.map(column => ({
          ...column,
          selected: true
        }))
        setTableColumns(prev => ({ ...prev, [tableName]: columnsWithSelection }))
      }
      return newSet
    })
  }, [setSelectedTables, setTableColumns, getTableColumns])

  const handleColumnToggle = useCallback((tableName, columnName) => {
    setTableColumns(prev => {
      const tableColumns = prev[tableName] || []
      const columnInfo = tableColumns.find(col => col.column === columnName || col.column_name === columnName)
      
      if (columnInfo) {
        const updatedColumns = tableColumns.map(col => 
          (col.column === columnName || col.column_name === columnName) 
            ? { ...col, selected: !col.selected }
            : col
        )
        return { ...prev, [tableName]: updatedColumns }
      }
      return prev
    })
  }, [setTableColumns])

  const handleTableExpand = useCallback(tableName => {
    setExpandedTables(prev => {
      const newSet = new Set(prev)
      if (newSet.has(tableName)) {
        newSet.delete(tableName)
      } else {
        newSet.add(tableName)
      }
      return newSet
    })
  }, [setExpandedTables])

  if (!selectedTool) {
    return <ErrorState title="No Tool Selected" message="Please select a tool in the previous step." />
  }
  
  if (!selectedSourcePlugin) {
    return <ErrorState 
      title="Source Plugin Not Selected" 
      message="Please go back to the Source Configuration step and select a source plugin before proceeding to table selection." 
    />
  }

  if (isLoadingConnection || isLoadingSchema) {
    return <LoadingState title="Loading Schema..." message="Fetching database schema information..." />
  }

  if (connectionError || schemaError) {
    return (
      <div className='space-y-6'>
        <div className='bg-red-50 border border-red-200 rounded-lg p-4'>
          <div className='flex'>
            <ExclamationTriangleIcon className='h-5 w-5 text-red-400 mr-2' />
            <div>
              <h4 className='text-sm font-medium text-red-900'>Schema Error</h4>
              <p className='text-sm text-red-700 mt-1'>{connectionError || schemaError}</p>
            </div>
          </div>
        </div>
      </div>
    )
  }

  const availableTables = getAllTables()
  if (availableTables.length === 0) {
    return (
      <div className='space-y-6'>
        <div className='bg-yellow-50 border border-yellow-200 rounded-lg p-4'>
          <div className='flex'>
            <ExclamationTriangleIcon className='h-5 w-5 text-yellow-400 mr-2' />
            <div>
              <h4 className='text-sm font-medium text-yellow-900'>No Tables Found</h4>
              <p className='text-sm text-yellow-700 mt-1'>
                No tables found in the database schema. Please check your connection settings or ensure the database contains tables.
              </p>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className='space-y-6'>
      <ConfigHeader 
        title="Table Selection"
        message="Select the tables you want to include in your data pipeline"
      />

      <div className='space-y-4'>
        <div className='flex justify-between items-center'>
          <div className='flex-1 max-w-md'>
            <input
              type='text'
              placeholder='Search tables...'
              value={searchTerm}
              onChange={e => setSearchTerm(e.target.value)}
              className='w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            />
          </div>
          <div className='flex items-center space-x-2'>
            <label className='flex items-center'>
              <input
                type='checkbox'
                checked={selectedTables.size === availableTables.length}
                onChange={e => handleSelectAll(e.target.checked)}
                className='rounded border-gray-300 text-blue-600 focus:ring-blue-500'
              />
              <span className='ml-2 text-sm text-gray-700'>Select All</span>
            </label>
          </div>
        </div>

        <div className='space-y-2 max-h-96 overflow-y-auto border border-gray-200 rounded-md p-4'>
          {availableTables
            .filter(table => 
              !searchTerm || 
              table.name.toLowerCase().includes(searchTerm.toLowerCase())
            )
            .map(table => (
              <div key={table.name} className='border border-gray-200 rounded-lg p-3'>
                <div className='flex items-center justify-between'>
                  <label className='flex items-center space-x-2 cursor-pointer'>
                    <input
                      type='checkbox'
                      checked={selectedTables.has(table.name)}
                      onChange={() => handleTableToggle(table.name)}
                      className='rounded border-gray-300 text-blue-600 focus:ring-blue-500'
                    />
                    <span className='text-sm font-medium text-gray-900'>{table.name}</span>
                  </label>
                  <button
                    onClick={() => handleTableExpand(table.name)}
                    className='text-blue-600 hover:text-blue-800 text-sm'
                  >
                    {expandedTables.has(table.name) ? 'Hide' : 'Show'} Columns
                  </button>
                </div>
                
                {expandedTables.has(table.name) && (
                  <div className='mt-3 pl-6 space-y-2'>
                    {tableColumns[table.name]?.map(column => (
                      <label key={column.column || column.column_name} className='flex items-center space-x-2 cursor-pointer'>
                        <input
                          type='checkbox'
                          checked={column.selected || false}
                          onChange={() => handleColumnToggle(table.name, column.column || column.column_name)}
                          className='rounded border-gray-300 text-blue-600 focus:ring-blue-500'
                        />
                        <span className='text-sm text-gray-700'>
                          {column.column || column.column_name}
                          {column.data_type && (
                            <span className='text-gray-500 ml-1'>({column.data_type})</span>
                          )}
                        </span>
                      </label>
                    ))}
                  </div>
                )}
              </div>
            ))}
        </div>
        
        {selectedTables.size > 0 && (
          <div className='text-sm text-gray-600'>
            Selected: {selectedTables.size} of {availableTables.length} tables
          </div>
        )}
      </div>
    </div>
  )
}

export default TableSelectionStep
