
import {
  pipelineAPI as pipelineApiFunctions,
  handleApiError
} from '../utils/api'

class PipelineAPI {
  async getPipelines (userId, params = {}) {
    try {
      const apiParams = {}
      
      const page = params.page || 1
      const pageSize = params.page_size || 10
      apiParams.offset = (page - 1) * pageSize
      apiParams.limit = pageSize
      
      if (userId !== undefined && userId !== null) apiParams.user_id = userId
      if (params.deprecated !== undefined) apiParams.deprecated = params.deprecated
      if (params.name && params.name.trim() !== '') apiParams.name = params.name
      if (params.created_date) apiParams.created_date = params.created_date

      const response = await pipelineApiFunctions.getPipelines(userId, apiParams)
      return response.data
    } catch (error) {
      throw handleApiError(error)
    }
  }

  async getPipelineById (id) {
    if (id === null || id === undefined) {
      throw new Error('Pipeline id is required')
    }
    try {
      const response = await pipelineApiFunctions.getPipelineById(id)
      return response.data
    } catch (error) {
      throw handleApiError(error)
    }
  }

  async getUserPipelines (userId) {
    try {
      const response = await pipelineApiFunctions.getUserPipelines(userId)
      return response.data
    } catch (error) {
      throw handleApiError(error)
    }
  }

  async createPipeline (pipelineData) {
    try {
      const response = await pipelineApiFunctions.createPipeline(pipelineData)
      return response.data
    } catch (error) {
      throw handleApiError(error)
    }
  }

  async updatePipeline (id, pipelineData) {
    try {
      const response = await pipelineApiFunctions.updatePipeline(
        id,
        pipelineData
      )
      return response.data
    } catch (error) {
      throw handleApiError(error)
    }
  }

  async deletePipeline (id) {
    try {
      const response = await pipelineApiFunctions.deletePipeline(id)
      return response.data
    } catch (error) {
      throw handleApiError(error)
    }
  }

  async getDatabaseSchema (connectionData) {
    try {
      const response = await pipelineApiFunctions.getSchemaInfo(connectionData)
      return response.data
    } catch (error) {
      throw handleApiError(error)
    }
  }

  async testConnection (connectionData) {
    try {
      const response = await pipelineApiFunctions.testConnection(connectionData)
      return response.data
    } catch (error) {
      throw handleApiError(error)
    }
  }
}

export const pipelineAPI = new PipelineAPI()
export { PipelineAPI }
