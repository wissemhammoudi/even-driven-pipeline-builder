
import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import useAuthStore from '../../store/authStore'
import LoginForm from '../../components/features/Auth/LoginForm'
import { validateRequired } from '../../utils/validation'

const LoginPage = () => {
  const navigate = useNavigate()
  const { login, isAuthenticated, isLoading } = useAuthStore()

  const [formData, setFormData] = useState({
    username: '',
    password: ''
  })
  const [errors, setErrors] = useState({})
  const [showPassword, setShowPassword] = useState(false)
  const [loginError, setLoginError] = useState('')

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard')
    }
  }, [isAuthenticated, navigate])

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
    if (loginError) {
      setLoginError('')
    }
  }

  const validateForm = () => {
    const newErrors = {}
    const usernameError = validateRequired(formData.username, 'Username')
    const passwordError = validateRequired(formData.password, 'Password')
    if (usernameError) newErrors.username = usernameError
    if (passwordError) newErrors.password = passwordError
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async e => {
    e.preventDefault()
    setLoginError('')
    if (!validateForm()) {
      return
    }
    try {
      const result = await login(formData)
      if (result && result.success) {
        navigate('/')
      } else {
        const errorMessage =
          result?.error?.response?.data?.detail ||
          result?.error?.message ||
          'Invalid username or password'
        setLoginError(errorMessage)
      }
    } catch (error) {
      const errorMessage =
        error?.response?.data?.detail ||
        error?.message ||
        'An unexpected error occurred during login'
      setLoginError(errorMessage)
    }
  }

  return (
    <LoginForm
      formData={formData}
      errors={errors}
      showPassword={showPassword}
      isLoading={isLoading}
      loginError={loginError}
      onInputChange={handleInputChange}
      onSubmit={handleSubmit}
      onToggleShowPassword={() => setShowPassword(v => !v)}
    />
  )
}

export default LoginPage