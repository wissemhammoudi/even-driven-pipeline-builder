import React from 'react'
import Input from '../../common/Input/Input'
import Button from '../../common/Button/Button'

const ProfileInfoEdit = ({ formData, errors, onChange, onSubmit, isLoading, onCancel }) => (
  <form onSubmit={onSubmit} className='space-y-4 mt-4'>
    <div className='grid grid-cols-1 md:grid-cols-2 gap-4'>
      <Input
        label='Username'
        type='text'
        name='username'
        value={formData.username}
        onChange={onChange}
        error={errors.username}
      />
      <Input
        label='Email'
        type='email'
        name='email'
        value={formData.email}
        onChange={onChange}
        error={errors.email}
      />
      <Input
        label='First Name'
        type='text'
        name='first_name'
        value={formData.first_name}
        onChange={onChange}
        error={errors.first_name}
      />
      <Input
        label='Last Name'
        type='text'
        name='last_name'
        value={formData.last_name}
        onChange={onChange}
        error={errors.last_name}
      />
    </div>
    <div className='flex space-x-2'>
      <Button
        type='submit'
        variant='primary'
        loading={isLoading}
        disabled={isLoading}
      >
        Save Changes
      </Button>
      <Button
        type='button'
        onClick={onCancel}
        variant='secondary'
      >
        Cancel
      </Button>
    </div>
  </form>
)

export default ProfileInfoEdit 