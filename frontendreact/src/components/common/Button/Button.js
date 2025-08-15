import React from 'react'

const baseStyles = {
  primary:
    'bg-primary text-white hover:bg-primary/90 font-medium',
  secondary:
    'bg-gray-100 text-gray-700 hover:bg-gray-200 font-medium',
  text:
    'bg-transparent text-primary hover:underline font-medium',
}

const Button = ({
  children,
  type = 'button',
  onClick,
  className = '',
  loading = false,
  disabled = false,
  variant = 'primary',
  icon: Icon,
  iconPosition = 'left',
  ...props
}) => {
  const isDisabled = disabled || loading
  const variantClass = baseStyles[variant] || baseStyles.primary
  return (
    <button
      type={type}
      onClick={onClick}
      className={`px-4 py-2 rounded-md shadow-sm transition-colors ${variantClass} ${isDisabled ? 'opacity-50 cursor-not-allowed' : ''} ${className}`}
      disabled={isDisabled}
      {...props}
    >
      {loading ? (
        <span className='inline-block w-4 h-4 border-2 border-t-2 border-gray-200 border-t-primary-500 rounded-full animate-spin mr-2'></span>
      ) : null}
      {Icon && iconPosition === 'left' && <Icon className='inline-block h-5 w-5 mr-2' />}
      {children}
      {Icon && iconPosition === 'right' && <Icon className='inline-block h-5 w-5 ml-2' />}
    </button>
  )
}

export default Button 