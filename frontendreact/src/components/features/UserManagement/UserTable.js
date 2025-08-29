import React from 'react'
import UserRow from './UserRow'

const UserTable = ({
  users,
  title,
  onEdit,
  onDelete,
  selectedUsers,
  onUserSelection,
  onSelectAll,
  isAdmin
}) => {
  if (users.length === 0) {
    return (
      <div className='text-center py-8'>
        <p className='text-gray-500'>No users found.</p>
      </div>
    )
  }

  return (
    <div className='space-y-4'>
      <h3 className='text-lg font-medium text-gray-900'>{title}</h3>
      <div className='overflow-hidden'>
        <table className='min-w-full divide-y divide-gray-200'>
          <thead className='bg-gray-50'>
            <tr>
              <th className='px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-12'>
                <input
                  type="checkbox"
                  checked={selectedUsers.length === users.length && users.length > 0}
                  onChange={(e) => onSelectAll(e.target.checked)}
                  className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                />
              </th>
              <th className='px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider'>
                User
              </th>
              <th className='px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider'>
                Email
              </th>
              <th className='px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider'>
                Role
              </th>
              <th className='px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider'>
                Status
              </th>
              <th className='px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider'>
                Created
              </th>
              <th className='px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider'>
                Actions
              </th>
            </tr>
          </thead>
          <tbody className='bg-white divide-y divide-gray-200'>
            {users.map(user => (
              <UserRow
                key={user.user_id}
                user={user}
                onEdit={onEdit}
                onDelete={onDelete}
                selected={selectedUsers.includes(user.user_id)}
                onSelectionChange={(checked) => onUserSelection(user.user_id, checked)}
                isAdmin={isAdmin}
              />
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default UserTable
