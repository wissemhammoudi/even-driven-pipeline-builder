import {
  CheckCircleIcon,
  XCircleIcon,
  ExclamationTriangleIcon,
  ClockIcon
} from '@heroicons/react/24/outline'

export const getStatusIcon = (status) => {
  switch (status) {
    case 'running':
      return CheckCircleIcon
    case 'stopped':
      return ExclamationTriangleIcon
    case 'broken':
      return XCircleIcon
    default:
      return ClockIcon
  }
}

export const getStatusColor = (status) => {
  switch (status) {
    case 'running':
      return 'bg-green-100 text-green-800'
    case 'stopped':
      return 'bg-yellow-100 text-yellow-800'
    case 'broken':
      return 'bg-red-100 text-red-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

export const getStatusIconComponent = (status) => {
  switch (status) {
    case 'running':
      return CheckCircleIcon
    case 'stopped':
      return ExclamationTriangleIcon
    case 'broken':
      return XCircleIcon
    default:
      return ClockIcon
  }
} 