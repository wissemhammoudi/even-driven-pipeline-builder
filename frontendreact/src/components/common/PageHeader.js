import React from 'react'
import Button from './Button/Button'

const PageHeader = ({
  title = '',
  subtitle = '',
  actions = null,
  onBackClick,
  backIcon: BackIcon,
  className = '',
  backButtonClassName = '',
  backIconClassName = '',
  children
}) => {
  return (
    <div className={`flex flex-col gap-2 mb-4 ${className}`}>
      <div className='flex items-center justify-between'>
        <div className='flex items-center space-x-4'>
          {onBackClick && BackIcon && (
            <Button
              onClick={onBackClick}
              className={`p-2 rounded-lg transition-colors ${backButtonClassName}`}
              icon={BackIcon}
              iconPosition='left'
              variant='secondary'
              iconClassName={backIconClassName}
            />
          )}
          <div>
            {title && <h1 className='text-3xl font-bold text-primary-900'>{title}</h1>}
            {subtitle && <p className='text-secondary-700'>{subtitle}</p>}
          </div>
        </div>
        {actions && <div className='flex space-x-3'>{actions}</div>}
      </div>
      {children}
    </div>
  )
}

export default PageHeader
