import { api } from '../utils/api'

class TransformationAPI {
  async createTransformation(transformationData) {
    try {
      const response = await api.post('/api/v1/transformation/create-transformation', transformationData)
      return response.data
    } catch (error) {
      throw error
    }
  }
}

export const transformationAPI = new TransformationAPI() 
