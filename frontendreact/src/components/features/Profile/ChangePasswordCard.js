import React, { useState } from 'react'
import {
  LockClosedIcon,
  EyeIcon,
  EyeSlashIcon
} from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'
import { userAPI } from '../../../api/userApi'
import { validateRequired, validatePassword, validatePasswordMatch } from '../../../utils/validation'
import Button from '../../common/Button/Button'
import Card from '../../common/Card/Card'
import Input from '../../common/Input/Input'

const ChangePasswordCard = ({ user }) => {
  const [isLoading, setIsLoading] = useState(false)
  const [showChangePassword, setShowChangePassword] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [showNewPassword, setShowNewPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)

  const [formData, setFormData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: ''
  })

  const [errors, setErrors] = useState({})

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

  const validatePasswordForm = () => {
    const newErrors = {}
    const currentPasswordError = validateRequired(formData.current_password, 'Current password')
    const newPasswordError = validatePassword(formData.new_password)
    const confirmPasswordError = validatePasswordMatch(formData.new_password, formData.confirm_password)
    if (currentPasswordError) newErrors.current_password = currentPasswordError
    if (newPasswordError) newErrors.new_password = newPasswordError
    if (confirmPasswordError) newErrors.confirm_password = confirmPasswordError
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handlePasswordSubmit = async e => {
    e.preventDefault()

    if (!user || !user.user_id) {
      toast.error('User not authenticated. Please log in again.')
      return
    }

    if (!validatePasswordForm()) return

    setIsLoading(true)

    try {
      const updateData = {
        user_id: user.user_id,
        old_password: formData.current_password,
        new_password: formData.new_password
      }

      const response = await userAPI.changePassword(updateData)

      if (response && (response.message || response.detail)) {
        toast.success('Password changed successfully!')
        setFormData(prev => ({
          ...prev,
          current_password: '',
          new_password: '',
          confirm_password: ''
        }))
        setShowChangePassword(false)
      } else {
        toast.error('Unexpected response from server')
      }
    } catch (error) {
      toast.error(
        error.response?.data?.detail ||
          error.message ||
          'Failed to change password'
      )
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Card>
      <div className='flex items-center justify-between mb-4'>
        <div className='flex items-center'>
          <LockClosedIcon className='h-6 w-6 text-primary-600 mr-2' />
          <span className='text-lg font-semibold text-primary-900'>
            Change Password
          </span>
        </div>
        <Button
          onClick={() => setShowChangePassword(!showChangePassword)}
          variant='primary'
        >
          {showChangePassword ? 'Cancel' : 'Change Password'}
        </Button>
      </div>

      {showChangePassword && (
        <form
          onSubmit={handlePasswordSubmit}
          className='space-y-4 mt-4 max-w-md'
        >
          <div>
            <Input
              label='Current Password'
              type={showPassword ? 'text' : 'password'}
              name='current_password'
              value={formData.current_password}
              onChange={handleInputChange}
              error={errors.current_password}
              icon={showPassword ? EyeSlashIcon : EyeIcon}
              iconPosition='right'
              onIconClick={() => setShowPassword(!showPassword)}
              autoComplete='current-password'
            />
          </div>
          <div>
            <Input
              label='New Password'
              type={showNewPassword ? 'text' : 'password'}
              name='new_password'
              value={formData.new_password}
              onChange={handleInputChange}
              error={errors.new_password}
              icon={showNewPassword ? EyeSlashIcon : EyeIcon}
              iconPosition='right'
              onIconClick={() => setShowNewPassword(!showNewPassword)}
              autoComplete='new-password'
            />
          </div>
          <div>
            <Input
              label='Confirm New Password'
              type={showConfirmPassword ? 'text' : 'password'}
              name='confirm_password'
              value={formData.confirm_password}
              onChange={handleInputChange}
              error={errors.confirm_password}
              icon={showConfirmPassword ? EyeSlashIcon : EyeIcon}
              iconPosition='right'
              onIconClick={() => setShowConfirmPassword(!showConfirmPassword)}
              autoComplete='new-password'
            />
          </div>

          <div className='flex space-x-2'>
            <Button
              type='submit'
              variant='primary'
              loading={isLoading}
              disabled={isLoading}
            >
              Change Password
            </Button>
            <Button
              type='button'
              onClick={() => setShowChangePassword(false)}
              variant='secondary'
            >
              Cancel
            </Button>
          </div>
        </form>
      )}
    </Card>
  )
}

export default ChangePasswordCard
