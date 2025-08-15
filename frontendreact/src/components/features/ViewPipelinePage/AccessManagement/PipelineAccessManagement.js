import React from 'react'
import { UsersIcon } from '@heroicons/react/24/outline'
import Button from '../../../common/Button/Button'
import AccessTable from './AccessTable'
import BulkGrantModal from './BulkGrantModal'
import Modal from '../../../common/Modal/Modal'
import { usePipelineAccessManagement } from './usePipelineAccessManagement'

const PipelineAccessManagement = ({ pipelineId, currentUserId }) => {
  const {
    users,
    nonAdminUsers,
    usersWithAccess,
    loading,
    showBulkModal,
    setShowBulkModal,
    selectedUsers,
    setSelectedUsers,
    bulkGrantType,
    setBulkGrantType,
    editingAccess,
    setEditingAccess,
    editGrantType,
    setEditGrantType,
    accessDenied,
    isBulkGranting,
    pendingRevokeUserId,
    setPendingRevokeUserId,
    handleBulkGrantAccess,
    handleRevokeAccess,
    confirmRevokeAccess,
    handleStartEdit,
    handleSaveEdit,
    handleCancelEdit,
    getUserById,
    availableUsers
  } = usePipelineAccessManagement(pipelineId, currentUserId)

  if (loading) {
    return (
      <div className='animate-pulse space-y-4'>
        <div className='h-8 bg-gray-200 rounded w-1/3'></div>
        <div className='space-y-3'>
          <div className='h-20 bg-gray-200 rounded-lg'></div>
          <div className='h-20 bg-gray-200 rounded-lg'></div>
          <div className='h-20 bg-gray-200 rounded-lg'></div>
        </div>
      </div>
    )
  }

  return (
    <div className='space-y-6'>
      <div className='flex flex-wrap gap-3'>
        <Button
          onClick={() => setShowBulkModal(true)}
          icon={UsersIcon}
          iconPosition='left'
          variant='secondary'
        >
          Bulk Grant
        </Button>
      </div>

      <AccessTable
        accesses={usersWithAccess}
        getUserById={getUserById}
        editingAccess={editingAccess}
        editGrantType={editGrantType}
        onStartEdit={handleStartEdit}
        onSaveEdit={handleSaveEdit}
        onCancelEdit={handleCancelEdit}
        onRevokeAccess={handleRevokeAccess}
        setEditGrantType={setEditGrantType}
        accessDenied={accessDenied}
      />

      <BulkGrantModal
        showModal={showBulkModal}
        availableUsers={availableUsers}
        nonAdminUsers={nonAdminUsers}
        selectedUsers={selectedUsers}
        bulkGrantType={bulkGrantType}
        isBulkGranting={isBulkGranting}
        onClose={() => setShowBulkModal(false)}
        onBulkGrantAccess={handleBulkGrantAccess}
        setSelectedUsers={setSelectedUsers}
        setBulkGrantType={setBulkGrantType}
      />

      <Modal
        isOpen={pendingRevokeUserId !== null}
        onClose={() => setPendingRevokeUserId(null)}
        title="Confirm Revoke Access"
        size="sm"
      >
        <div>Are you sure you want to revoke access for this user?</div>
        <div className="flex justify-end mt-4 space-x-2">
          <Button
            onClick={() => setPendingRevokeUserId(null)}
            variant='secondary'
          >
            Cancel
          </Button>
          <Button
            onClick={confirmRevokeAccess}
            variant='primary'
            className='bg-red-600 hover:bg-red-700 focus:ring-red-500'
          >
            Revoke
          </Button>
        </div>
      </Modal>
    </div>
  )
}

export default PipelineAccessManagement 