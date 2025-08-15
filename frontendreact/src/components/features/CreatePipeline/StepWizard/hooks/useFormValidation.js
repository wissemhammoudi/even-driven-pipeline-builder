import { StepTypeEnum, ToolEnum } from '../utils'

export function useFormValidation() {
  const validateCurrentStep = (currentStep, formData, selectedSourcePlugin, selectedDestinationPlugin, selectedTables) => {
    if (formData.type === StepTypeEnum.DATA_TRANSFORMATION) {
      switch (currentStep) {
        case 1:
          return formData.name.trim()
        case 2:
          const hasUtilityType = formData.step_config.utility_type
          const hasDestinationConfig = (
            formData.step_config.destination_config &&
            Object.keys(formData.step_config.destination_config).length > 0
          )
          const isValid = hasUtilityType && hasDestinationConfig
          
          return isValid
        case 3:
          return true
        case 4:
          return true
        default:
          return false
      }
    } else if (formData.type === StepTypeEnum.DATA_VISUALIZATION) {
      switch (currentStep) {
        case 1:
          return formData.name.trim()
        case 2:
          const hasDestinationConfig = (
            formData.step_config.destination_config &&
            Object.keys(formData.step_config.destination_config).length > 0
          )
          return hasDestinationConfig
        case 3:
          return true
        default:
          return false
      }
    } else {
      switch (currentStep) {
        case 1:
          return (
            formData.name.trim() &&
            formData.step_config.tool
          )
        case 2:
          return selectedSourcePlugin && hasSourceConnectionConfig(formData)
        case 3:
          return selectedDestinationPlugin && hasDestinationConnectionConfig(formData)
        case 4:
          return selectedTables.size > 0
        case 5:
          return true
        default:
          return false
      }
    }
  }

  const hasSourceConnectionConfig = (formData) => {
    const tool = formData.step_config.tool
    if (tool === ToolEnum.MELTANO) {
      return hasConnectionConfig(formData, 'extractor')
    } else if (tool === ToolEnum.DLT) {
      return hasConnectionConfig(formData, 'source')
    }
    return false
  }

  const hasDestinationConnectionConfig = (formData) => {
    const tool = formData.step_config.tool
    if (tool === ToolEnum.MELTANO) {
      return hasConnectionConfig(formData, 'loader')
    } else if (tool === ToolEnum.DLT) {
      return hasConnectionConfig(formData, 'destination')
    }
    return false
  }

  const hasConnectionConfig = (formData, section) => {
    const config = formData.step_config.connection_config[section] || {}
    return (
      Object.keys(config).length > 0 &&
      (config.host || config.database || config.dbname) &&
      (config.user || config.username) &&
      config.password
    )
  }

  return {
    validateCurrentStep,
    hasSourceConnectionConfig,
    hasDestinationConnectionConfig,
    hasConnectionConfig
  }
} 