import { dashboardAPI, handleApiError } from '../utils/api'

class DashboardApi {
  async getDashboardData (userId) {
    try {
      if (!userId) {
        throw new Error('User ID is required')
      }
      const response = await dashboardAPI.getDashboardData(userId)
      return response.data
    } catch (error) {
      throw handleApiError(error)
    }
  }

  async getChartsData (userId, days = 7) {
    try {
      if (!userId) {
        throw new Error('User ID is required')
      }
      const response = await dashboardAPI.getChartsData(userId, days)
      return response.data
    } catch (error) {
      throw handleApiError(error)
    }
  }

  async getPipelineAnalytics (pipelineId, days = 30) {
    try {
      if (!pipelineId) {
        throw new Error('Pipeline ID is required')
      }
      const response = await dashboardAPI.getPipelineAnalytics(pipelineId, days)
      return response.data
    } catch (error) {
      throw handleApiError(error)
    }
  }
}

const dashboardApi = new DashboardApi()
export default dashboardApi
