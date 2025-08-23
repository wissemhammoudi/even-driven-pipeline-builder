import React from 'react'

const ProfileInfoView = ({ user }) => (
  <div className='grid grid-cols-1 md:grid-cols-2 gap-4'>
    <div>
      <span className='font-medium'>Username:</span> 
      <span className='ml-2 text-gray-700'>{user?.username || 'Not set'}</span>
    </div>
    <div>
      <span className='font-medium'>Email:</span> 
      <span className='ml-2 text-gray-700'>{user?.email || 'Not set'}</span>
    </div>
    <div>
      <span className='font-medium'>First Name:</span> 
      <span className='ml-2 text-gray-700'>{user?.first_name || 'Not set'}</span>
    </div>
    <div>
      <span className='font-medium'>Last Name:</span> 
      <span className='ml-2 text-gray-700'>{user?.last_name || 'Not set'}</span>
    </div>
  </div>
)

export default ProfileInfoView 