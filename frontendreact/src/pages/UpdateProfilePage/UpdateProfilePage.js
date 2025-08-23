import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import useAuthStore from '../../store/authStore'
import ProfileInfoCard from '../../components/features/Profile/ProfileInfoCard'
import ChangePasswordCard from '../../components/features/Profile/ChangePasswordCard'
import PageHeader from '../../components/common/PageHeader'
import { ArrowLeftIcon } from '@heroicons/react/24/outline'
import { userAPI } from '../../api/userApi'
import toast from 'react-hot-toast'

const UpdateProfilePage = () => {
  const navigate = useNavigate()
  const { user, setUser } = useAuthStore()
  const [fullUserData, setFullUserData] = useState(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchUserData = async () => {
      if (user?.username) {
        try {
          setIsLoading(true)
          console.log('Fetching user data for:', user.username)
          const response = await userAPI.getUserByUsername(user.username)
          console.log('User data response:', response)
          if (response) {
            setFullUserData(response)
            setUser(response)
          }
        } catch (error) {
          console.error('Failed to fetch user data:', error)
          toast.error('Failed to load profile data')
        } finally {
          setIsLoading(false)
        }
      } else {
        console.log('No username found in user object:', user)
        setIsLoading(false)
      }
    }

    fetchUserData()
  }, [user?.username, setUser])

  const handleBackClick = () => {
    navigate('/dashboard')
  }

  if (isLoading) {
    return (
      <div className='max-w-3xl mx-auto space-y-8 p-6'>
        <div className='text-center'>
          <div className='animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto'></div>
          <p className='mt-4 text-gray-600'>Loading profile...</p>
        </div>
      </div>
    )
  }

  return (
    <div className='max-w-3xl mx-auto space-y-8 p-6'>
      <PageHeader
        title='Update Profile'
        subtitle={fullUserData ? `Editing profile for ${fullUserData.username}` : 'Loading...'}
        onBackClick={handleBackClick}
        backIcon={ArrowLeftIcon}
      />

      <ProfileInfoCard user={fullUserData} updateUser={setUser} />

      <ChangePasswordCard user={fullUserData} />
    </div>
  )
}

export default UpdateProfilePage
