import React from 'react'
import TableConfigCard from './TableConfigCard'

const Step3TableConfiguration = ({ 
  primaryTable, 
  selectedTargetTables, 
  tableConfigs, 
  getTableColumns, 
  onConfigChange, 
  onColumnToggle, 
  onBack, 
  onReset, 
  onComplete, 
  isStepComplete 
}) => (
  <div>
    <h6 className='font-medium text-gray-900 mb-4'>Step 3: Configure Each Target Table</h6>
    <p className='text-sm text-gray-600 mb-4'>
      Primary Table: <span className='font-medium'>{primaryTable}</span><br />
      Target Tables: <span className='font-medium'>{selectedTargetTables.join(', ')}</span>
    </p>
    
    <div className='space-y-6'>
      {selectedTargetTables.map(targetTable => (
        <TableConfigCard
          key={targetTable}
          targetTable={targetTable}
          config={tableConfigs[targetTable] || {}}
          primaryTable={primaryTable}
          getTableColumns={getTableColumns}
          onConfigChange={onConfigChange}
          onColumnToggle={onColumnToggle}
        />
      ))}
    </div>

    <div className='flex justify-between mt-6'>
      <button onClick={onBack} className='bg-gray-500 text-white px-4 py-2 rounded-md hover:bg-gray-600'>
        Back
      </button>
      <div className='flex space-x-2'>
        <button onClick={onReset} className='bg-gray-300 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-400'>
          Reset
        </button>
        <button
          onClick={onComplete}
          disabled={!isStepComplete()}
          className='bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed'
        >
          Create Joins
        </button>
      </div>
    </div>
  </div>
)

export default Step3TableConfiguration 