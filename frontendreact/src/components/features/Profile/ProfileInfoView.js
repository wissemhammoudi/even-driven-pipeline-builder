import React from 'react'

const ProfileInfoView = ({ user }) => (
  <div className='grid grid-cols-1 md:grid-cols-2 gap-4'>
    <div>
      <span className='font-medium'>Username:</span> {user?.username}
    </div>
    <div>
      <span className='font-medium'>Email:</span> {user?.email}
    </div>
    <div>
      <span className='font-medium'>First Name:</span> {user?.first_name}
    </div>
    <div>
      <span className='font-medium'>Last Name:</span> {user?.last_name}
    </div>
  </div>
)

export default ProfileInfoView 