import React from 'react'
import { ExclamationTriangleIcon } from '@heroicons/react/24/outline'
import AccessRow from './AccessRow'

const AccessTable = ({ 
  accesses, 
  getUserById, 
  editingAccess, 
  editGrantType, 
  onStartEdit, 
  onSaveEdit, 
  onCancelEdit, 
  onRevokeAccess, 
  setEditGrantType,
}) => {

  if (accesses.length === 0) {
    return (
      <div className='bg-gray-50 rounded-lg p-8 text-center'>
        <div className='text-gray-400 mb-4'>
          <ExclamationTriangleIcon className='h-12 w-12 mx-auto' />
        </div>
        <h3 className='text-lg font-medium text-gray-900 mb-2'>
          No Access Grants
        </h3>
        <p className='text-gray-500 mb-4'>
          No users have been granted access to this pipeline yet.
        </p>
      </div>
    )
  }

  return (
    <div className='bg-white shadow rounded-lg overflow-hidden'>
      <div className='px-6 py-4 border-b border-gray-200'>
        <h3 className='text-lg font-medium text-gray-900'>
          Current Access ({accesses.length} {accesses.length === 1 ? 'user' : 'users'})
        </h3>
        <p className='text-sm text-gray-500 mt-1'>
          Manage user access levels and permissions for this pipeline
        </p>
      </div>
      
      <div className='overflow-x-auto'>
        <table className='min-w-full divide-y divide-gray-200'>
          <thead className='bg-gray-50'>
            <tr>
              <th className='px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider'>
                User
              </th>
              <th className='px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider'>
                Access Level
              </th>
              <th className='px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider'>
                Granted Date
              </th>
              <th className='px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider'>
                Actions
              </th>
            </tr>
          </thead>
          <tbody className='bg-white divide-y divide-gray-200'>
            {accesses.map((access) => (
              <AccessRow
                key={access.access_id}
                access={access}
                getUserById={getUserById}
                editingAccess={editingAccess}
                editGrantType={editGrantType}
                onStartEdit={onStartEdit}
                onSaveEdit={onSaveEdit}
                onCancelEdit={onCancelEdit}
                onRevokeAccess={onRevokeAccess}
                setEditGrantType={setEditGrantType}
              />
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default AccessTable 