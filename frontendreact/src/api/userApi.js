import { userAPI as userApiFunctions, handleApiError } from '../utils/api'

class UserAPI {
  async login (credentials) {
    try {
      const response = await userApiFunctions.login(credentials)
      return response.data
    } catch (error) {
      throw handleApiError(error)
    }
  }

  async updateProfile (profileData) {
    try {
      const response = await userApiFunctions.updateProfile(profileData)
      return response.data
    } catch (error) {
      throw handleApiError(error)
    }
  }

  async changePassword (passwordData) {
    try {
      const response = await userApiFunctions.updatePassword(passwordData)
      return response.data
    } catch (error) {
      throw handleApiError(error)
    }
  }

  async getUsers () {
    try {
      const response = await userApiFunctions.getUsers()
      return response.data
    } catch (error) {
      throw handleApiError(error)
    }
  }
}

export const userAPI = new UserAPI()

export { UserAPI }
