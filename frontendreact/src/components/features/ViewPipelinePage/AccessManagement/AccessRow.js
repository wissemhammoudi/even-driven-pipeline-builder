import React from 'react'
import {
  EyeIcon,
  ShieldCheckIcon,
  TrashIcon,
  PencilIcon,
  CheckIcon,
  XMarkIcon
} from '@heroicons/react/24/outline'

const AccessRow = ({ 
  access, 
  getUserById, 
  editingAccess, 
  editGrantType, 
  onStartEdit, 
  onSaveEdit, 
  onCancelEdit, 
  onRevokeAccess, 
  setEditGrantType 
}) => {
  const user = getUserById(access.user_id)
  
  if (!user) {
    return null
  }

  const getAccessIcon = (grantType) => {
    switch (grantType) {
      case 'EDIT':
        return <PencilIcon className='h-4 w-4' />
      case 'ADMIN':
        return <ShieldCheckIcon className='h-4 w-4' />
      default:
        return <PencilIcon className='h-4 w-4' />
    }
  }

  const getAccessColor = (grantType) => {
    switch (grantType) {
      case 'EDIT':
        return 'bg-green-100 text-green-800'
      case 'ADMIN':
        return 'bg-purple-100 text-purple-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const formatTimestamp = (timestamp) => {
    if (!timestamp) return 'N/A'
    return new Date(timestamp).toLocaleDateString()
  }

  return (
    <tr key={access.access_id} className='hover:bg-gray-50'>
      <td className='px-6 py-4 whitespace-nowrap'>
        <div className='flex items-center'>
          <div className='h-10 w-10 flex-shrink-0'>
            <div className='h-10 w-10 rounded-full bg-gray-300 flex items-center justify-center'>
              <span className='text-sm font-medium text-gray-700'>
                {user.first_name?.charAt(0)}{user.last_name?.charAt(0)}
              </span>
            </div>
          </div>
          <div className='ml-4'>
            <div className='text-sm font-medium text-gray-900'>
              {user.first_name} {user.last_name}
            </div>
            <div className='text-sm text-gray-500'>{user.email}</div>
          </div>
        </div>
      </td>
      <td className='px-6 py-4 whitespace-nowrap'>
        {editingAccess === access.access_id ? (
          <select
            value={editGrantType}
            onChange={(e) => setEditGrantType(e.target.value)}
            className='block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm'
          >
            <option value='EDIT'>Edit</option>
            <option value='ADMIN'>Admin</option>
          </select>
        ) : (
          <span
            className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getAccessColor(
              access.grant_type
            )}`}
          >
            {getAccessIcon(access.grant_type)}
            <span className='ml-1'>{access.grant_type}</span>
          </span>
        )}
      </td>
      <td className='px-6 py-4 whitespace-nowrap text-sm text-gray-500'>
        {formatTimestamp(access.granted_at)}
      </td>
      <td className='px-6 py-4 whitespace-nowrap text-right text-sm font-medium'>
        {editingAccess === access.access_id ? (
          <div className='flex items-center space-x-2'>
            <button
              onClick={() => onSaveEdit(access.access_id)}
              className='text-green-600 hover:text-green-900 p-1 rounded'
              title='Save changes'
            >
              <CheckIcon className='h-4 w-4' />
            </button>
            <button
              onClick={onCancelEdit}
              className='text-gray-600 hover:text-gray-900 p-1 rounded'
              title='Cancel editing'
            >
              <XMarkIcon className='h-4 w-4' />
            </button>
          </div>
        ) : (
          <div className='flex items-center space-x-2'>
            <button
              onClick={() => onStartEdit(access.access_id, access.grant_type)}
              className='text-blue-600 hover:text-blue-900 p-1 rounded'
              title='Edit access level'
            >
              <PencilIcon className='h-4 w-4' />
            </button>
            <button
              onClick={() => onRevokeAccess(access.user_id)}
              className='text-red-600 hover:text-red-900 p-1 rounded'
              title='Revoke access'
            >
              <TrashIcon className='h-4 w-4' />
            </button>
          </div>
        )}
      </td>
    </tr>
  )
}

export default AccessRow 