import React, { useState } from 'react'
import Card from '../../common/Card/Card'
import Button from '../../common/Button/Button'

const SchemaChangeAlert = ({ breakingChanges, schemaChanges }) => {
  const [showNonBreaking, setShowNonBreaking] = useState(true)
  const isBlockedByBreakingChange = breakingChanges && breakingChanges.length > 0

  // Helper to extract human_readable_message
  const getMessage = (change) => {
    if (typeof change === 'string') return change
    if (change && change.human_readable_message) return change.human_readable_message
    if (change && change.payload) {
      try {
        const payload = typeof change.payload === 'string' ? JSON.parse(change.payload) : change.payload
        if (payload && payload.human_readable_message) return payload.human_readable_message
      } catch {}
    }
    return JSON.stringify(change)
  }

  // Only show non-breaking changes if not blocked by breaking changes and user hasn't dismissed
  const showSchemaInfo = schemaChanges && schemaChanges.length > 0 && !isBlockedByBreakingChange && showNonBreaking
  // Show breaking changes if present (cannot be dismissed)
  const showBreakingInfo = isBlockedByBreakingChange

  return (
    <>
      {/* Show non-breaking schema changes if any and not blocked by breaking change */}
      {showSchemaInfo && (
        <Card className='mb-4 border-blue-200'>
          <div className='flex items-start'>
            <div className='flex-1'>
              <div className='text-blue-800 font-bold mb-2'>Schema Changes Detected:</div>
              <ul className='list-disc pl-6 mb-2 text-blue-800'>
                {schemaChanges.map((change, idx) => (
                  <li key={idx} className='mb-1'>{getMessage(change)}</li>
                ))}
              </ul>
              <div className='bg-green-50 border border-green-200 text-green-800 px-4 py-2 rounded mt-2'>
                <strong className='font-bold'>No Breaking Changes Detected.</strong>
              </div>
            </div>
            <Button
              variant='text'
              className='ml-4 text-blue-800 hover:text-blue-600 font-bold text-lg px-2 focus:outline-none'
              onClick={() => setShowNonBreaking(false)}
              title='Dismiss'
            >
              ×
            </Button>
          </div>
        </Card>
      )}
      {/* Show breaking changes if any, in a non-dismissible card, pipeline remains blocked */}
      {showBreakingInfo && (
        <Card className='mb-4 border-red-400'>
          <div className='text-red-700 font-bold mb-2'>Pipeline Blocked: Breaking Schema Changes Detected</div>
          <ul className='list-disc pl-6 mt-2 text-red-700'>
            {breakingChanges.map((change, idx) => (
              <li key={idx} className='mb-1'>{getMessage(change)}</li>
            ))}
          </ul>
          <div className='bg-red-200 border border-red-300 text-red-900 px-4 py-2 rounded mt-2'>
            <strong className='font-bold'>You must resolve these before running the pipeline.</strong>
          </div>
        </Card>
      )}
    </>
  )
}

export default SchemaChangeAlert 