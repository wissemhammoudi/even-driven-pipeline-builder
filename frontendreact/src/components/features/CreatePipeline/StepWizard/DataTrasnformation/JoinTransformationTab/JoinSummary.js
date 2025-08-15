import React from 'react'

const JoinSummary = ({ joinTransformations, onRemoveJoin, onClearAll }) => (
  <div className='bg-white border border-gray-200 rounded-lg p-4'>
    <div className='flex justify-between items-center mb-4'>
      <h6 className='font-medium text-gray-900'>Configured Joins</h6>
      {joinTransformations.length > 0 && (
        <button onClick={onClearAll} className='text-red-600 hover:text-red-800 text-sm'>
          Clear All
        </button>
      )}
    </div>

    {joinTransformations.length === 0 ? (
      <div className='text-center py-8 text-gray-500'>
        <p>No join transformations configured yet.</p>
        <p className='text-sm'>Create your first join above.</p>
      </div>
    ) : (
      <div className='space-y-3'>
        {joinTransformations.map((join, index) => (
          <div key={index} className='border border-gray-200 rounded-lg p-3'>
            <div className='flex justify-between items-start'>
              <div className='flex-1'>
                <h4 className='font-medium text-gray-900 mb-1'>{join.name}</h4>
                <p className='text-sm text-gray-600'>
                  Primary Table: <span className='font-medium'>{join.primary_table}</span>
                </p>
                {join.primary_table_columns && join.primary_table_columns.length > 0 && (
                  <p className='text-sm text-blue-600 mb-1'>
                    Primary columns: {join.primary_table_columns.join(', ')}
                  </p>
                )}
                {join.target_tables && join.target_tables.map((targetConfig, targetIndex) => (
                  <div key={targetIndex} className='mt-2 p-2 bg-gray-50 rounded'>
                    <p className='text-sm text-gray-600'>
                      {join.primary_table} {targetConfig.join_type} JOIN {targetConfig.target_table}
                    </p>
                    {targetConfig.join_conditions && targetConfig.join_conditions.map((condition, condIndex) => (
                      <p key={condIndex} className='text-sm text-gray-500'>
                        ON {join.primary_table}.{condition.source_column} = {targetConfig.target_table}.{condition.target_column}
                      </p>
                    ))}
                    {targetConfig.columns && targetConfig.columns.length > 0 && (
                      <p className='text-sm text-blue-600'>
                        Selected columns: {targetConfig.columns.join(', ')}
                      </p>
                    )}
                  </div>
                ))}
              </div>
              <button
                onClick={() => onRemoveJoin(index)}
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
)

export default JoinSummary 