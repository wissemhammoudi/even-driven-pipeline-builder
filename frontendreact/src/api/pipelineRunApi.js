import {
  pipelineRunsAPI,
  supersetAPI,
  handleApiError
} from '../utils/api'

class PipelineRunAPI {
  async getPipelineRunsByPipelineId (pipelineId) {
    try {
      const response = await pipelineRunsAPI.getPipelineRunsByPipelineId(pipelineId)
      return response.data
    } catch (error) {
      throw handleApiError(error)
    }
  }

  async startPipeline (pipelineId, userId) {
    try {
      const response = await pipelineRunsAPI.startPipeline(pipelineId, userId)
      return response.data
    } catch (error) {
      throw handleApiError(error)
    }
  }

  async startVisualization(pipelineId, userId) {
    try {
      const response = await supersetAPI.startVisualization({
        pipeline_id: pipelineId,
        user_id: userId
      })
      return response.data
    } catch (error) {
      throw handleApiError(error)
    }
  }
}

export const pipelineRunAPI = new PipelineRunAPI()
export { PipelineRunAPI } 