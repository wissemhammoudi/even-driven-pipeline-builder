import {
  CircleStackIcon,
  DocumentTextIcon,
  CalendarIcon,
  LinkIcon,
  CogIcon
} from '@heroicons/react/24/outline'
import { StepTypeEnum } from '../CreatePipeline/StepWizard/utils'
export const getTransformationIcon = iconName => {
  const iconClasses = 'h-6 w-6 text-primary'

  switch (iconName) {
    case 'database':
      return <CircleStackIcon className={iconClasses} />
    case 'document-text':
      return <DocumentTextIcon className={iconClasses} />
    case 'calendar':
      return <CalendarIcon className={iconClasses} />
    case 'link':
      return <LinkIcon className={iconClasses} />
    default:
      return <CogIcon className={iconClasses} />
  }
}

export const getTransformationIconName = funcName => {
  const icons = {
    null_Value: 'database',
    string_transform: 'document-text',
    date_transform: 'calendar',
    lookup_join: 'link',
  }
  return icons[funcName] || 'cog'
}

export const processTransformationsFromConfig = (selectedTool, toolConfigs) => {
  if (!selectedTool || !toolConfigs.length) return []

  const transformations = []

  const transformationConfigs = toolConfigs.filter(
    config =>
      config.type === StepTypeEnum.DATA_TRANSFORMATION && config.config?.transformation
  )

  transformationConfigs.forEach(config => {
    const transformationConfig = config.config.transformation

    if (Array.isArray(transformationConfig)) {
      transformationConfig.forEach(funcGroup => {
        Object.entries(funcGroup).forEach(([funcName, funcOptions]) => {
          if (typeof funcOptions === 'object' && funcOptions !== null) {
            const transformationInfo = {
              name: funcName
                .replace(/_/g, ' ')
                .replace(/\b\w/g, l => l.toUpperCase()),
              description: `Available ${funcName.replace(
                /_/g,
                ' '
              )} transformations`,
              icon: getTransformationIconName(funcName),
              functions: []
            }

            Object.entries(funcOptions).forEach(([option, supportedTypes]) => {
              if (Array.isArray(supportedTypes)) {
                const functionInfo = {
                  name: option,
                  syntax: `${funcName}:${option}`,
                  supported_types: supportedTypes,
                  description: `Apply ${option} function for ${funcName.replace(
                    /_/g,
                    ' '
                  )}`
                }
                transformationInfo.functions.push(functionInfo)
              }
            })

            if (transformationInfo.functions.length > 0) {
              transformations.push(transformationInfo)
            }
          }
        })
      })
    }
  })

  return transformations
}
