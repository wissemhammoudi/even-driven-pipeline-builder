import React from 'react'

const Step1BasicInfo = ({ 
  modelName, 
  setModelName, 
  primaryTable, 
  setPrimaryTable, 
  availableTables, 
  onNext 
}) => (
  <div>
    <h6 className='font-medium text-gray-900 mb-4'>Step 1: Select Model Name and Primary Table</h6>
    <div className='grid grid-cols-1 md:grid-cols-2 gap-4 mb-4'>
      <div>
        <label className='block text-sm font-medium text-gray-700 mb-2'>Model Name</label>
        <input
          type='text'
          value={modelName}
          onChange={e => setModelName(e.target.value)}
          placeholder='e.g., stations_locations_join'
          className='block w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
        />
        <p className='text-xs text-gray-500 mt-1'>This will be the name of the generated join model file.</p>
      </div>
      <div>
        <label className='block text-sm font-medium text-gray-700 mb-2'>Primary Table</label>
        <select
          value={primaryTable}
          onChange={e => setPrimaryTable(e.target.value)}
          className='block w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
        >
          <option value=''>Select primary table...</option>
          {availableTables.map(table => (
            <option key={table.name} value={table.name}>{table.name}</option>
          ))}
        </select>
      </div>
    </div>
    <div className='flex justify-end'>
      <button
        onClick={onNext}
        disabled={!primaryTable || !modelName.trim()}
        className='bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed'
      >
        Next: Select Target Tables
      </button>
    </div>
  </div>
)

export default Step1BasicInfo 