import React, { useState } from 'react'
import {
  PencilIcon as Edit,
  TrashIcon as Trash2,
  UserIcon,
  ShieldCheckIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline'
import Button from '../../common/Button/Button'
import DeleteConfirmModal from '../../common/Modal/DeleteConfirmModal'
import { UserRole } from '../../../utils/userRoles'

const UserRow = ({
  user,
  onEdit,
  onDelete,
  selected,
  onSelectionChange,
  isAdmin
}) => {
  const [showDeleteModal, setShowDeleteModal] = useState(false)

  const getRoleIcon = (role) => {
    switch (role) {
      case UserRole.ADMIN:
        return <ShieldCheckIcon className='h-5 w-5 text-blue-500' />
      case UserRole.USER:
        return <UserIcon className='h-5 w-5 text-gray-500' />
      default:
        return <UserIcon className='h-5 w-5 text-gray-400' />
    }
  }

  const getStatusIcon = (isDeleted) => {
    if (isDeleted) {
      return <ExclamationTriangleIcon className='h-5 w-5 text-red-500' />
    }
    return <div className='h-2 w-2 bg-green-500 rounded-full'></div>
  }

  return (
    <>
      <tr className='hover:bg-gray-50'>
        <td className='px-6 py-4 whitespace-nowrap'>
          <input
            type="checkbox"
            checked={selected}
            onChange={(e) => onSelectionChange(e.target.checked)}
            className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
          />
        </td>
        <td className='px-6 py-4 whitespace-nowrap'>
          <div className='flex items-center'>
            <div className='flex-shrink-0 h-10 w-10'>
              {getRoleIcon(user.role)}
            </div>
            <div className='ml-4'>
              <div className='text-sm font-medium text-gray-900'>
                {user.first_name && user.last_name 
                  ? `${user.first_name} ${user.last_name}`
                  : user.username
                }
              </div>
              <div className='text-sm text-gray-500'>
                @{user.username}
              </div>
            </div>
          </div>
        </td>
        <td className='px-6 py-4 whitespace-nowrap text-sm text-gray-900'>
          {user.email}
        </td>
        <td className='px-6 py-4 whitespace-nowrap'>
          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
            user.role === UserRole.ADMIN 
              ? 'bg-blue-100 text-blue-800' 
              : 'bg-gray-100 text-gray-800'
          }`}>
            {user.role}
          </span>
        </td>
        <td className='px-6 py-4 whitespace-nowrap'>
          <div className='flex items-center'>
            {getStatusIcon(user.is_deleted)}
            <span className={`ml-2 inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
              user.is_deleted 
                ? 'bg-red-100 text-red-800' 
                : 'bg-green-100 text-green-800'
            }`}>
              {user.is_deleted ? 'Deleted' : 'Active'}
            </span>
          </div>
        </td>
        <td className='px-6 py-4 whitespace-nowrap text-sm text-gray-500'>
          {new Date(user.created_at).toLocaleDateString()}
        </td>
        <td className='px-6 py-4 whitespace-nowrap text-right text-sm font-medium'>
          <div className='flex items-center justify-end space-x-2'>
            <Button
              onClick={() => onEdit(user)}
              className='p-1 border border-transparent rounded-full text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500'
              title='Edit User'
              variant='text'
            >
              <Edit className='h-4 w-4' />
            </Button>
            <Button
              onClick={() => setShowDeleteModal(true)}
              className='p-1 border border-transparent rounded-full text-gray-400 hover:text-red-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500'
              title='Delete User'
              variant='text'
            >
              <Trash2 className='h-4 w-4' />
            </Button>
          </div>
        </td>
      </tr>
      <DeleteConfirmModal
        isOpen={showDeleteModal}
        onClose={() => setShowDeleteModal(false)}
        onConfirm={() => {
          setShowDeleteModal(false)
          onDelete(user.user_id)
        }}
        itemName={user.username}
        loading={false}
      />
    </>
  )
}

export default UserRow
