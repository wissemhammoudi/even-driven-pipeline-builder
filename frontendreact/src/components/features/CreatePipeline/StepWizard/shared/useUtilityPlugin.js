import { useState, useEffect } from 'react'

export const useUtilityPlugin = (plugins, onPluginSelection, selectedTool) => {
  const [utilityType, setUtilityType] = useState('')
  
  const toolPlugins = plugins?.[selectedTool] || {}
  const utilityPlugins = toolPlugins.utility || toolPlugins.utilities || []

  useEffect(() => {
    if (!utilityType && utilityPlugins.length > 0) {
      const defaultUtility = utilityPlugins[0]
      if (defaultUtility) {
        setUtilityType(defaultUtility.name)
        onPluginSelection('utility', defaultUtility.name)
      }
    }
  }, [utilityPlugins, utilityType, onPluginSelection])

  const handleUtilityTypeChange = (newUtilityType) => {
    setUtilityType(newUtilityType)
    if (newUtilityType) {
      onPluginSelection('utility', newUtilityType)
    }
  }

  return {
    utilityType,
    utilityPlugins,
    setUtilityType: handleUtilityTypeChange
  }
} 