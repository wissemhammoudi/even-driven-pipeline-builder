import React, { forwardRef } from 'react'

const Input = forwardRef(
  (
    {
      label,
      error,
      type = 'text',
      name,
      value,
      onChange,
      className = '',
      placeholder = '',
      icon: Icon,
      iconPosition = 'left',
      onIconClick,
      ...props
    },
    ref
  ) => (
    <div className={`w-full ${className}`}>
      {label && (
        <label htmlFor={name} className='block text-sm font-medium mb-1'>
          {label}
        </label>
      )}
      <div className='relative'>
        {Icon && iconPosition === 'left' && (
          <span className={`absolute inset-y-0 left-0 pl-3 flex items-center ${onIconClick ? 'cursor-pointer' : 'pointer-events-none'}`}>
            <Icon 
              className='h-5 w-5 text-gray-400' 
              onClick={onIconClick}
            />
          </span>
        )}
        <input
          ref={ref}
          type={type}
          name={name}
          id={name}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          className={`w-full border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 ${
            error ? 'border-red-300 focus:ring-red-500 focus:border-red-500' : 'border-primary-300'
          } ${Icon ? (iconPosition === 'left' ? 'pl-10' : 'pr-10') : ''}`}
          aria-invalid={!!error}
          aria-describedby={error ? `${name}-error` : undefined}
          {...props}
        />
        {Icon && iconPosition === 'right' && (
          <span className={`absolute inset-y-0 right-0 pr-3 flex items-center ${onIconClick ? 'cursor-pointer' : 'pointer-events-none'}`}>
            <Icon 
              className='h-5 w-5 text-gray-400' 
              onClick={onIconClick}
            />
          </span>
        )}
      </div>
      {error && (
        <p className='mt-1 text-sm text-red-600' id={`${name}-error`}>
          {error}
        </p>
      )}
    </div>
  )
)

export default Input 
