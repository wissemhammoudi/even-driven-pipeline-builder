import { useState, useEffect, useCallback } from 'react'
import { stepConfigAPI } from '../../../../../utils/api'
import { StepTypeEnum } from '../utils'
export const useFunctionMapping = (utilityType) => {
  const [functionMapping, setFunctionMapping] = useState({})
  const [transformationSchema, setTransformationSchema] = useState({})
  const [isLoadingFunctions, setIsLoadingFunctions] = useState(false)
  const [functionLoadError, setFunctionLoadError] = useState(null)

  const getFunctionMapping = useCallback(async () => {
    if (!utilityType) return

    setIsLoadingFunctions(true)
    setFunctionLoadError(null)

    try {
      const response = await stepConfigAPI.getStepConfigsByTool(utilityType)

      if (response.data && response.data.length > 0) {
        const transformationConfig = response.data.find(config => 
          config.type === StepTypeEnum.DATA_TRANSFORMATION
        )

        if (transformationConfig) {
          const transformationSchema = transformationConfig.config?.transformation?.[0] || {}

          const mapping = {}

          Object.entries(transformationSchema).forEach(([category, functions]) => {
            if (typeof functions === 'object' && functions !== null) {
              Object.entries(functions).forEach(([funcName, supportedTypes]) => {
                if (Array.isArray(supportedTypes)) {
                  supportedTypes.forEach(type => {
                    if (!mapping[type]) {
                      mapping[type] = []
                    }
                    mapping[type].push(funcName)
                  })
                }
              })
            }
          })

          setFunctionMapping(mapping)
          setTransformationSchema(transformationSchema)
        } else {
          setFunctionLoadError(`No data transformation configuration found for ${utilityType}`)
        }
      } else {
        setFunctionLoadError(`No ${utilityType} configuration found`)
      }
    } catch (error) {
      setFunctionLoadError(
        error.response?.data?.message || 
        error.message || 
        'Failed to load function mapping.'
      )
    } finally {
      setIsLoadingFunctions(false)
    }
  }, [utilityType])

  useEffect(() => {
    if (utilityType) {
      getFunctionMapping()
    }
  }, [utilityType, getFunctionMapping])

  return {
    functionMapping,
    transformationSchema,
    isLoadingFunctions,
    functionLoadError,
    getFunctionMapping
  }
} 
