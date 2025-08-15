import React from 'react'
import { EyeIcon, EyeSlashIcon } from '@heroicons/react/24/outline'
import logo from '../../../assets/logo.svg'
import Button from '../../common/Button/Button'
import Input from '../../common/Input/Input'

const LoginForm = ({
  formData,
  errors,
  showPassword,
  isLoading,
  loginError,
  onInputChange,
  onSubmit,
  onToggleShowPassword
}) => (
  <div className='min-h-screen flex items-center justify-center bg-primary-50'>
    <div className='max-w-md w-full space-y-8 p-8'>
      <div className='text-center'>
        <img src={logo} alt='Logo' className='h-16 w-auto mx-auto mb-6' />
        <h2 className='text-3xl font-bold text-primary-900'>Sign in</h2>
      </div>
      {loginError && (
        <div className='text-red-600 text-center mb-4'>{loginError}</div>
      )}
      <form className='space-y-6' onSubmit={onSubmit}>
        <Input
          label='Username'
          name='username'
          type='text'
          required
          placeholder='Username'
          value={formData.username}
          onChange={onInputChange}
          error={errors.username}
        />
        <Input
          label='Password'
          name='password'
          type={showPassword ? 'text' : 'password'}
          required
          placeholder='Password'
          value={formData.password}
          onChange={onInputChange}
          error={errors.password}
          icon={showPassword ? EyeSlashIcon : EyeIcon}
          iconPosition='right'
          autoComplete='current-password'
        />
        <div>
          <Button
            type='submit'
            disabled={isLoading}
            loading={isLoading}
            className='w-full'
          >
            Sign In
          </Button>
        </div>
      </form>
    </div>
  </div>
)

export default LoginForm 