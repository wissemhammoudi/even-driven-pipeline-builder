import { stepConfigAPI } from '../utils/api'

export const stepConfigurationApi = {
  getStepTypes: async () => {
    try {
      const response = await stepConfigAPI.getStepConfigTypes()
      return response.data
    } catch (error) {
      return []
    }
  },

  getTools: async () => {
    try {
      const response = await stepConfigAPI.getStepConfigTools()
      return response.data
    } catch (error) {
      return []
    }
  },


  getToolsByType: async (type) => {
    try {
      const response = await stepConfigAPI.getStepConfigToolsByType(type)
      return response.data
    } catch (error) {
      return []
    }
  },

  getStepConfigs: async () => {
    try {
      const response = await stepConfigAPI.getStepConfigs()
      return response.data
    } catch (error) {
      return []
    }
  },

  getConfigsPerTool: async tool => {
    try {
      const response = await stepConfigAPI.getStepConfigsByTool(tool)
      return response.data
    } catch (error) {
      return []
    }
  },

  getConfigPerTool: async (tool, type, pluginType) => {
    try {
      const response = await stepConfigAPI.getConfigPerToolType(tool, type, pluginType);
      return response.data;
    } catch (error) {
      return [];
    }
  },

  deprecateStepConfig: async stepConfigId => {
    try {
      const response = await stepConfigAPI.deprecateStepConfig(stepConfigId)
      return response.status === 200
    } catch (error) {
      return false
    }
  }
}

export default stepConfigurationApi;
