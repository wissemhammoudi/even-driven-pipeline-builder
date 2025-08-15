import React from 'react';
import Modal from './Modal';
import Button from '../Button/Button';

const DeleteConfirmModal = ({
  isOpen,
  onClose,
  onConfirm,
  itemName = 'item',
  loading = false
}) => (
  <Modal
    isOpen={isOpen}
    onClose={onClose}
    title={`Delete Confirmation`}
    size='sm'
  >
    <div className='space-y-4'>
      <p>Are you sure you want to delete "{itemName}"?</p>
      <div className='flex justify-end space-x-2'>
        <Button
          onClick={onClose}
          variant='secondary'
          className='px-4'
        >
          Cancel
        </Button>
        <Button
          onClick={onConfirm}
          variant='danger'
          className='px-4'
          loading={loading}
          disabled={loading}
        >
          Delete
        </Button>
      </div>
    </div>
  </Modal>
);

export default DeleteConfirmModal; 