import React from 'react'

const Step2TableSelection = ({ 
  primaryTable, 
  modelName, 
  availableTables, 
  selectedTargetTables, 
  onTableToggle, 
  onBack, 
  onNext 
}) => (
  <div>
    <h6 className='font-medium text-gray-900 mb-4'>Step 2: Select Target Tables</h6>
    <p className='text-sm text-gray-600 mb-4'>
      Primary Table: <span className='font-medium'>{primaryTable}</span><br />
      Model Name: <span className='font-medium'>{modelName}</span>
    </p>
    <div className='mb-4'>
      <label className='block text-sm font-medium text-gray-700 mb-2'>Target Tables (Select multiple)</label>
      <div className='space-y-2 max-h-48 overflow-y-auto border border-gray-200 rounded-md p-3'>
        {availableTables
          .filter(table => table.name !== primaryTable)
          .map(table => (
            <label key={table.name} className='flex items-center space-x-2 cursor-pointer'>
              <input
                type='checkbox'
                checked={selectedTargetTables.includes(table.name)}
                onChange={() => onTableToggle(table.name)}
                className='rounded border-gray-300 text-blue-600 focus:ring-blue-500'
              />
              <span className='text-sm text-gray-700'>{table.name}</span>
            </label>
          ))}
      </div>
    </div>
    <div className='flex justify-between'>
      <button onClick={onBack} className='bg-gray-500 text-white px-4 py-2 rounded-md hover:bg-gray-600'>
        Back
      </button>
      <button
        onClick={onNext}
        disabled={selectedTargetTables.length === 0}
        className='bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed'
      >
        Next: Configure Each Table
      </button>
    </div>
  </div>
)

export default Step2TableSelection 