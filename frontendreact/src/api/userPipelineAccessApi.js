
import { userPipelineAccessAPI as userPipelineAccessApiFunctions, pipelineAPI, handleApiError } from '../utils/api'

class UserPipelineAccessAPI {
  async updateAccess(accessData, userId) {
    try {
      const response = await userPipelineAccessApiFunctions.updateAccess(accessData, userId)
      return response.data
    } catch (error) {
      throw handleApiError(error)
    }
  }

  async bulkGrantAccess(bulkData, userId) {
    try {
      const response = await userPipelineAccessApiFunctions.bulkGrantAccess(bulkData, userId)
      return response.data
    } catch (error) {
      throw handleApiError(error)
    }
  }

  async bulkRevokeAccess(bulkData, userId) {
    try {
      const response = await userPipelineAccessApiFunctions.bulkRevokeAccess(bulkData, userId)
      return response.data
    } catch (error) {
      throw handleApiError(error)
    }
  }

  async getUsersForPipeline(pipelineId, userId) {
    try {
      const response = await userPipelineAccessApiFunctions.getUsersForPipeline(pipelineId, userId)
      return response.data
    } catch (error) {
      throw handleApiError(error)
    }
  }

  async getUserPermissions(pipelineId, userId) {
    try {
      const response = await userPipelineAccessApiFunctions.getPipelinePermissions(pipelineId, userId)
      return response.data
    } catch (error) {
      if (error.response?.status === 404) {
        try {
          const pipelineResponse = await pipelineAPI.getPipelineById(pipelineId)
          const pipeline = pipelineResponse.data

          if (pipeline.created_by === userId) {
            return {
              can_view_pipeline: true,
              can_start_pipeline: true,
              can_start_visualization: true,
              can_manage_access: true,
              can_edit_pipeline: true,
              can_delete_pipeline: true
            }
          }
        } catch (pipelineError) {
          console.warn('Could not fetch pipeline info for permission fallback:', pipelineError)
        }

        return {
          can_view_pipeline: true,
          can_start_pipeline: false,
          can_start_visualization: false,
          can_manage_access: false,
          can_edit_pipeline: false,
          can_delete_pipeline: false
        }
      }

      throw handleApiError(error)
    }
  }
}

const userPipelineAccessAPI = new UserPipelineAccessAPI()
export default userPipelineAccessAPI
  