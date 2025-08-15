import React from 'react'

const TableConfigCard = ({ 
  targetTable, 
  config, 
  primaryTable, 
  getTableColumns, 
  onConfigChange, 
  onColumnToggle 
}) => {
  const isComplete = config.joinType && config.condition && config.selectedColumns && config.selectedColumns.length > 0

  return (
    <div className='border border-gray-200 rounded-lg p-4'>
      <div className='flex items-center justify-between mb-4'>
        <h4 className='font-medium text-gray-900'>{targetTable}</h4>
        {isComplete && (
          <span className='text-xs bg-green-100 text-green-700 px-2 py-1 rounded'>✓ Configured</span>
        )}
      </div>
      
      <div className='grid grid-cols-1 md:grid-cols-2 gap-4 mb-4'>
        <div>
          <label className='block text-sm font-medium text-gray-700 mb-2'>Join Type</label>
          <select
            value={config.joinType || ''}
            onChange={e => onConfigChange(targetTable, 'joinType', e.target.value)}
            className='block w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
          >
            <option value=''>Select join type...</option>
            <option value='INNER'>INNER JOIN</option>
            <option value='LEFT'>LEFT JOIN</option>
            <option value='RIGHT'>RIGHT JOIN</option>
            <option value='FULL'>FULL JOIN</option>
          </select>
        </div>
        
        <div>
          <label className='block text-sm font-medium text-gray-700 mb-2'>Join Condition</label>
          <div className='grid grid-cols-3 gap-2'>
            <select
              value={config.condition?.split(' = ')[0] || ''}
              onChange={e => {
                const targetCol = config.condition?.split(' = ')[1] || ''
                onConfigChange(targetTable, 'condition', `${e.target.value} = ${targetCol}`)
              }}
              className='block w-full px-2 py-2 text-sm border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            >
              <option value=''>Primary col...</option>
              {getTableColumns(primaryTable).map(col => (
                <option key={col} value={`${primaryTable}.${col}`}>{col}</option>
              ))}
            </select>
            <div className='flex items-center justify-center'>
              <span className='text-gray-500 text-sm'>=</span>
            </div>
            <select
              value={config.condition?.split(' = ')[1] || ''}
              onChange={e => {
                const primaryCol = config.condition?.split(' = ')[0] || ''
                onConfigChange(targetTable, 'condition', `${primaryCol} = ${e.target.value}`)
              }}
              className='block w-full px-2 py-2 text-sm border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            >
              <option value=''>Target col...</option>
              {getTableColumns(targetTable).map(col => (
                <option key={col} value={`${targetTable}.${col}`}>{col}</option>
              ))}
            </select>
          </div>
          {config.condition && (
            <p className='text-xs text-gray-500 mt-1'>
              Condition: <span className='font-mono'>{config.condition}</span>
            </p>
          )}
        </div>
      </div>
      
      <div>
        <label className='block text-sm font-medium text-gray-700 mb-2'>
          Select Columns from {targetTable}
        </label>
        <div className='space-y-2 max-h-32 overflow-y-auto border border-gray-200 rounded-md p-3'>
          {getTableColumns(targetTable).map(columnName => (
            <label key={columnName} className='flex items-center space-x-2 cursor-pointer'>
              <input
                type='checkbox'
                checked={config.selectedColumns?.includes(columnName) || false}
                onChange={() => onColumnToggle(targetTable, columnName)}
                className='rounded border-gray-300 text-blue-600 focus:ring-blue-500'
              />
              <span className='text-sm text-gray-700'>{columnName}</span>
            </label>
          ))}
        </div>
        {config.selectedColumns && config.selectedColumns.length > 0 && (
          <p className='text-xs text-gray-500 mt-2'>
            Selected: <span className='font-medium'>{config.selectedColumns.join(', ')}</span>
          </p>
        )}
      </div>
    </div>
  )
}

export default TableConfigCard 