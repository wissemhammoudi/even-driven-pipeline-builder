import { useState, useCallback } from 'react'
import { transformationAPI } from '../api/transformationApi'

export const useTransformation = () => {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)

  const createTransformation = useCallback(async transformationData => {
    setIsLoading(true)
    setError(null)

    try {
      const result = await transformationAPI.createTransformation(
        transformationData
      )
      return { success: true, data: result }
    } catch (err) {
      const errorMessage = err.message || 'Failed to create transformation'
      setError(errorMessage)
      return { success: false, error: errorMessage }
    } finally {
      setIsLoading(false)
    }
  }, [])



  const clearError = useCallback(() => {
    setError(null)
  }, [])

  return {
    isLoading,
    error,
    createTransformation,
    clearError
  }
}
