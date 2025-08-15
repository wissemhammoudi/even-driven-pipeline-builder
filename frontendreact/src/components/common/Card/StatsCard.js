import React from 'react'

const colorClasses = {
  primary: 'border-primary-100 text-primary-500',
  green: 'border-green-100 text-green-500',
  red: 'border-red-100 text-red-500',
  gray: 'border-gray-100 text-gray-500'
}

const textClasses = {
  primary: 'text-primary-900',
  green: 'text-green-900',
  red: 'text-red-900',
  gray: 'text-gray-900'
}

const labelClasses = {
  primary: 'text-secondary-600',
  green: 'text-green-600',
  red: 'text-red-600',
  gray: 'text-gray-600'
}

const subtitleClasses = {
  primary: 'text-primary',
  green: 'text-green-500',
  red: 'text-red-500',
  gray: 'text-gray-500'
}

const iconClasses = {
  primary: 'text-primary-500',
  green: 'text-green-500',
  red: 'text-red-500',
  gray: 'text-gray-500'
}

const StatCard = ({
  title,
  value,
  subtitle,
  icon: Icon,
  color = 'primary',
  iconPosition = 'left',
  className = ''
}) => {
  return (
    <div className={`bg-white shadow rounded-lg border ${colorClasses[color]} ${className}`}>
      <div className='p-5'>
        <div className={`flex items-center ${iconPosition === 'right' ? 'flex-row-reverse' : ''}`}>
          {Icon && (
            <div className='flex-shrink-0'>
              <Icon className={`h-8 w-8 ${iconClasses[color]}`} />
            </div>
          )}
          <div className={`ml-5 w-0 flex-1 ${iconPosition === 'right' ? 'mr-5 ml-0' : ''}`}>
            <dl>
              <dt className={`text-sm font-medium truncate ${labelClasses[color]}`}>{title}</dt>
              <dd className={`text-lg font-medium ${textClasses[color]}`}>{value}</dd>
              {subtitle && <dd className={`text-sm ${subtitleClasses[color]}`}>{subtitle}</dd>}
            </dl>
          </div>
        </div>
      </div>
    </div>
  )
}

export default StatCard
