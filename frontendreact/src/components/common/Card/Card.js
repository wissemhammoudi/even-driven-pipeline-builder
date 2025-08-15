import React from 'react'

const Card = ({ children, className = '', header, footer, ...props }) => (
  <div className={`bg-white shadow rounded-xl border border-gray-100 p-6 ${className}`} {...props}>
    {header && <div className='mb-4'>{header}</div>}
    {children}
    {footer && <div className='mt-4'>{footer}</div>}
  </div>
)

export default Card 