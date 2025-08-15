import React from 'react'
import Modal from '../../../common/Modal/Modal'
import Button from '../../../common/Button/Button'

const BulkGrantModal = ({
  showModal,
  availableUsers,
  nonAdminUsers,
  selectedUsers,
  bulkGrantType,
  isBulkGranting,
  onClose,
  onBulkGrantAccess,
  setSelectedUsers,
  setBulkGrantType
}) => {
  const handleUserToggle = (userId, checked) => {
    if (checked) {
      setSelectedUsers([...selectedUsers, userId.toString()])
    } else {
      setSelectedUsers(selectedUsers.filter(id => id !== userId.toString()))
    }
  }

  const handleSelectAll = () => {
    if (selectedUsers.length === availableUsers.length) {
      setSelectedUsers([])
    } else {
      setSelectedUsers(availableUsers.map(user => user.user_id.toString()))
    }
  }

  return (
    <Modal isOpen={showModal} onClose={onClose} title="Bulk Grant Access" size="md">
      <div className='space-y-6'>
        <div>
          <div className='flex items-center justify-between mb-2'>
            <label className='block text-sm font-medium text-gray-700'>
              Select Users ({selectedUsers.length} selected)
            </label>
            {availableUsers.length > 0 && (
              <Button
                onClick={handleSelectAll}
                variant='text'
                className='text-sm text-blue-600 hover:text-blue-800 px-0'
              >
                {selectedUsers.length === availableUsers.length ? 'Deselect All' : 'Select All'}
              </Button>
            )}
          </div>
          <div className='max-h-48 overflow-y-auto border border-gray-300 rounded-lg p-3 bg-gray-50'>
            {availableUsers.length === 0 ? (
              <p className='text-sm text-gray-500 text-center py-4'>
                {nonAdminUsers.length > 0 
                  ? 'All non-admin users already have access to this pipeline.'
                  : 'No non-admin users available.'
                }
              </p>
            ) : (
              availableUsers.map(user => (
                <label
                  key={user.user_id}
                  className='flex items-center space-x-3 py-2 hover:bg-white rounded px-2 transition-colors cursor-pointer'
                >
                  <input
                    type='checkbox'
                    checked={selectedUsers.includes(user.user_id.toString())}
                    onChange={e => handleUserToggle(user.user_id, e.target.checked)}
                    className='rounded border-gray-300 text-blue-600 focus:ring-blue-500'
                  />
                  <div className='flex-1 min-w-0'>
                    <p className='text-sm font-medium text-gray-900 truncate'>
                      {user.first_name} {user.last_name}
                    </p>
                    <p className='text-xs text-gray-500 truncate'>
                      {user.email}
                    </p>
                  </div>
                </label>
              ))
            )}
          </div>
        </div>

        <div>
          <label className='block text-sm font-medium text-gray-700 mb-2'>
            Access Level
          </label>
          <select
            value={bulkGrantType}
            onChange={e => setBulkGrantType(e.target.value)}
            className='block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
          >
            <option value='EDIT'>
              Edit - Can view and run pipeline
            </option>
            <option value='ADMIN'>
              Admin - Can view, edit, and manage access
            </option>
          </select>
        </div>
      </div>

      <div className='flex justify-end space-x-3 mt-8'>
        <Button
          onClick={onClose}
          variant='secondary'
        >
          Cancel
        </Button>
        <Button
          onClick={onBulkGrantAccess}
          disabled={selectedUsers.length === 0 || isBulkGranting}
          variant='primary'
        >
          {isBulkGranting 
            ? 'Granting...' 
            : `Grant Access to ${selectedUsers.length} User${selectedUsers.length !== 1 ? 's' : ''}`
          }
        </Button>
      </div>
    </Modal>
  )
}

export default BulkGrantModal 