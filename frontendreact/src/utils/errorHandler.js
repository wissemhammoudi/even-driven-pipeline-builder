export const extractErrorMessage = (error, defaultMessage = 'An error occurred') => {
  if (!error) {
    return defaultMessage
  }

  if (typeof error === 'string') {
    return error
  }

  if (error && typeof error === 'object') {
    const message = error.message || error.detail || error.error 
    
    if (message) {
      return message
    }

    try {
      const errorString = JSON.stringify(error)
      if (errorString && errorString !== '{}') {
        return errorString
      }
    } catch {
    }
  }

  return defaultMessage
}

export const handleApiError = (error, defaultMessage = 'Operation failed', toastError = null) => {
  const errorMessage = extractErrorMessage(error, defaultMessage)
  
  if (toastError && typeof toastError === 'function') {
    toastError(errorMessage)
  }
  
  return { 
    success: false, 
    error: errorMessage 
  }
}

export const handleAsyncError = async (asyncFn, defaultMessage = 'Operation failed', toastError = null) => {
  try {
    const result = await asyncFn()
    return { success: true, data: result }
  } catch (error) {
    return handleApiError(error, defaultMessage, toastError)
  }
}