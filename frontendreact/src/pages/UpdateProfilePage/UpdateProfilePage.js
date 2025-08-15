import React from 'react'
import { useNavigate } from 'react-router-dom'
import useAuthStore from '../../store/authStore'
import ProfileInfoCard from '../../components/features/Profile/ProfileInfoCard'
import ChangePasswordCard from '../../components/features/Profile/ChangePasswordCard'
import PageHeader from '../../components/common/PageHeader'
import { ArrowLeftIcon } from '@heroicons/react/24/outline'

const UpdateProfilePage = () => {
  const navigate = useNavigate()
  const { user, setUser } = useAuthStore()

  const handleBackClick = () => {
    navigate('/dashboard')
  }

  return (
    <div className='max-w-3xl mx-auto space-y-8 p-6'>
      <PageHeader
        title='Update Profile'
        subtitle={user ? `Editing profile for ${user.username}` : ''}
        onBackClick={handleBackClick}
        backIcon={ArrowLeftIcon}
      />

      <ProfileInfoCard user={user} updateUser={setUser} />

      <ChangePasswordCard user={user} />
    </div>
  )
}

export default UpdateProfilePage
