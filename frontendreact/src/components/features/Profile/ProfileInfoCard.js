import React, { useState, useEffect } from 'react'
import { UserIcon } from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'
import { userAPI } from '../../../api/userApi'
import { validateRequired, validateEmail } from '../../../utils/validation'
import Button from '../../common/Button/Button'
import Card from '../../common/Card/Card'
import ProfileInfoView from './ProfileInfoView'
import ProfileInfoEdit from './ProfileInfoEdit'

const ProfileInfoCard = ({ user, updateUser }) => {
  const [isLoading, setIsLoading] = useState(false)
  const [showEditInfo, setShowEditInfo] = useState(false)

  const [formData, setFormData] = useState({
    username: user?.username || '',
    email: user?.email || '',
    first_name: user?.first_name || '',
    last_name: user?.last_name || ''
  })

  useEffect(() => {
    if (user) {
      setFormData({
        username: user.username || '',
        email: user.email || '',
        first_name: user.first_name || '',
        last_name: user.last_name || ''
      })
    }
  }, [user])

  const [errors, setErrors] = useState({})

  useEffect(() => {
    if (user) {
      setFormData({
        username: user.username || '',
        email: user.email || '',
        first_name: user.first_name || '',
        last_name: user.last_name || ''
      })
    }
  }, [user])

  const handleInputChange = e => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))

    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }))
    }
  }

  const validateInfoForm = () => {
    const newErrors = {}
    const usernameError = validateRequired(formData.username, 'Username')
    const emailError = validateEmail(formData.email)
    const firstNameError = validateRequired(formData.first_name, 'First name')
    const lastNameError = validateRequired(formData.last_name, 'Last name')
    if (usernameError) newErrors.username = usernameError
    if (emailError) newErrors.email = emailError
    if (firstNameError) newErrors.first_name = firstNameError
    if (lastNameError) newErrors.last_name = lastNameError
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleInfoSubmit = async e => {
    e.preventDefault()

    if (!user || !user.user_id) {
      toast.error('User not authenticated. Please log in again.')
      return
    }

    if (!validateInfoForm()) return

    setIsLoading(true)

    try {
      const updateData = {
        user_id: user.user_id,
        username: formData.username,
        email: formData.email,
        first_name: formData.first_name,
        last_name: formData.last_name
      }

      const response = await userAPI.updateProfile(updateData)

      if (response && (response.message || response.detail)) {
        try {
          const updatedUserResponse = await userAPI.getUserByUsername(formData.username)
          if (updatedUserResponse) {
            const updatedUser = updatedUserResponse
            
            localStorage.setItem('user', JSON.stringify(updatedUser))

            if (updateUser) {
              updateUser(updatedUser)
            }

            toast.success('Profile updated successfully!')
            setShowEditInfo(false)
          } else {
            toast.error('Failed to fetch updated profile data')
          }
        } catch (fetchError) {
          console.error('Failed to fetch updated user data:', fetchError)
          const updatedUser = {
            ...user,
            username: formData.username,
            email: formData.email,
            first_name: formData.first_name,
            last_name: formData.last_name
          }

          localStorage.setItem('user', JSON.stringify(updatedUser))

          if (updateUser) {
            updateUser(updatedUser)
          }

          toast.success('Profile updated successfully!')
          setShowEditInfo(false)
        }
      } else {
        toast.error('Unexpected response from server')
      }
    } catch (error) {
      toast.error(
        error.response?.data?.detail ||
          error.message ||
          'Failed to update profile'
      )
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Card>
      <div className='flex items-center justify-between mb-4'>
        <div className='flex items-center'>
          <UserIcon className='h-6 w-6 text-primary-600 mr-2' />
          <span className='text-lg font-semibold text-primary-900'>
            Profile Information
          </span>
        </div>
        <Button
          onClick={() => setShowEditInfo(!showEditInfo)}
          variant='primary'
        >
          {showEditInfo ? 'Cancel' : 'Edit Information'}
        </Button>
      </div>
      {showEditInfo ? (
        <ProfileInfoEdit
          formData={formData}
          errors={errors}
          onChange={handleInputChange}
          onSubmit={handleInfoSubmit}
          isLoading={isLoading}
          onCancel={() => setShowEditInfo(false)}
        />
      ) : (
        <ProfileInfoView user={user} />
      )}
    </Card>
  )
}

export default ProfileInfoCard