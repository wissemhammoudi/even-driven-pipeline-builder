import axios from 'axios'
import { API_CONFIG } from './config'

export const apiClient = axios.create(API_CONFIG)

apiClient.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

apiClient.interceptors.response.use(
  response => {
    return response
  },
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      localStorage.setItem('login_status', 'loggedout')
      window.location.href = '/login'
    } else if (error.response?.status === 403) {
    } else if (error.response?.status === 500) {
    }
    return Promise.reject(error)
  }
)

export const handleApiError = error => {
  if (error.response) {
    const { status, data } = error.response
    return {
      status,
      message: data?.detail || data?.message || `HTTP ${status} error`,
      data
    }
  } else if (error.request) {
    return {
      status: 0,
      message: 'Network error - no response received',
      data: null
    }
  } else {
    return {
      status: 0,
      message: error.message || 'Unknown error occurred',
      data: null
    }
  }
}

export const hasRequiredRole = (userRole, requiredRole) => {
  if (requiredRole === 'admin') {
    return userRole === 'admin'
  } else if (requiredRole === 'user') {
    return userRole === 'user' || userRole === 'admin'
  }
  return false
}

export const getUserRole = () => {
  try {
    const user = JSON.parse(localStorage.getItem('user') || '{}')
    return user.role || user.mapped_role || null
  } catch {
    return null
  }
}

export const api = {
  get: (url, config = {}) => apiClient.get(url, config),
  post: (url, data = {}, config = {}) => apiClient.post(url, data, config),
  put: (url, data = {}, config = {}) => apiClient.put(url, data, config),
  patch: (url, data = {}, config = {}) => apiClient.patch(url, data, config),
  delete: (url, config = {}) => apiClient.delete(url, config)
}

export const userAPI = {
  login: credentials => api.post('/api/v1/users/login', credentials),
  getCurrentUser: () => api.get('/api/v1/users/me'),
  updateProfile: data => api.patch('/api/v1/users/', data),
  updatePassword: data => api.patch('/api/v1/users/password', data),
  getUsers: () => api.get('/api/v1/users/'),
  getUserByUsername: username => api.get(`/api/v1/users/${username}`),
}

export const stepConfigAPI = {
  getStepConfigs: () => api.get('/api/v1/stepConfig/'),
  getStepConfigsByTool: tool => api.get(`/api/v1/stepConfig/configpertool?tool=${tool}`),
  getStepConfigTypes: () => api.get('/api/v1/stepConfig/types'),
  getStepConfigTools: () => api.get('/api/v1/stepConfig/toolsname'),
  getStepConfigToolsByType: type => api.get(`/api/v1/stepConfig/tools?type=${type}`),
  deprecateStepConfig: (id) => api.put(`/api/v1/stepConfig/${id}/deprecate`),
  getConfigPerToolType: (tool, type, pluginType) =>
    api.get('/api/v1/stepConfig/configpertooltype', {
      params: { tool, type, pluginType }
    })
}

export const userPipelineAccessAPI = {
  updateAccess: (data, userId) => api.put(`/api/v1/user-pipeline-access/update?user_id=${userId}`, data),
  bulkGrantAccess: (data, userId) => api.post(`/api/v1/user-pipeline-access/bulk-grant?user_id=${userId}`, data),
  bulkRevokeAccess: (data, userId) => api.post(`/api/v1/user-pipeline-access/bulk-revoke?user_id=${userId}`, data),
  getUsersForPipeline: (pipelineId, userId) => api.get(`/api/v1/user-pipeline-access/pipeline/${pipelineId}/users?user_id=${userId}`),
  getPipelinePermissions: (pipelineId, userId) => api.get(`/api/v1/user-pipeline-access/pipeline/${pipelineId}/permissions/${userId}`),
}

export const pipelineAPI = {
  getSchemaInfo: schemaData => api.post('/api/v1/pipeline/schema', schemaData),
  testConnection: connectionData => api.post('/api/v1/pipeline/test-connection', connectionData),
  getPipelines: (userId, params = {}) => {
    const queryParams = new URLSearchParams()
    queryParams.append('user_id', userId)
    if (params.offset !== undefined) queryParams.append('offset', params.offset)
    if (params.limit !== undefined) queryParams.append('limit', params.limit)
    if (params.deprecated !== undefined) queryParams.append('deprecated', params.deprecated)
    if (params.name) queryParams.append('name', params.name)
    if (params.created_date) queryParams.append('created_date', params.created_date)
    return api.get(`/api/v1/pipeline/?${queryParams.toString()}`)
  },
  getUserPipelines: userId => api.get(`/api/v1/pipeline/user/${userId}`),
  createPipeline: data => api.post('/api/v1/pipeline/', data, { timeout: 1200000 }),
  updatePipeline: data => api.patch('/api/v1/pipeline/', data),
  getPipelineById: id => api.get(`/api/v1/pipeline/${id}`),
  deletePipeline: id => api.delete(`/api/v1/pipeline/${id}`),
  getPipelineSteps: pipelineId => api.get(`/api/v1/pipeline/${pipelineId}/steps`),
  getPipelineStepsDetails: pipelineId => api.get(`/api/v1/pipeline/${pipelineId}/steps/details`),
}

export const pipelineRunsAPI = {
  getPipelineRunsByPipelineId: (pipelineId) => api.get(`/api/v1/pipeline-runs/pipeline/${pipelineId}`),
  startPipeline: (pipelineId, userId) => api.post('/api/v1/pipeline-runs/start', { pipeline_id: pipelineId, user_id: userId }, { timeout: 600000 }),
}

export const transformationAPI = {
  createTransformation: data => api.post('/api/v1/transformations/', data)
}

export const dashboardAPI = {
  getDashboardData: (userId) => {
    const queryParams = new URLSearchParams()
    queryParams.append('user_id', userId)
    return api.get(`/api/v1/dashboard/?${queryParams.toString()}`)
  },
  getChartsData: (userId, days = 7) => {
    const queryParams = new URLSearchParams()
    queryParams.append('user_id', userId)
    queryParams.append('days', days)
    return api.get(`/api/v1/dashboard/charts?${queryParams.toString()}`)
  },
  getPipelineAnalytics: (pipelineId, days = 30) => {
    const queryParams = new URLSearchParams()
    queryParams.append('days', days)
    return api.get(`/api/v1/pipeline-dashboard/pipeline/${pipelineId}/analytics?${queryParams.toString()}`)
  }
}

export const supersetAPI = {
  startVisualization: data =>
    api.post('/api/v1/superset/visualization/start', data)
}

export const schemaChangeAPI = {
  getSchemaChanges: (pipelineId) => api.get(`/schema-changes/detect`),
  getBreakingChanges: (pipelineId) => api.get(`/schema-changes/detect`)
}

export const cdcAPI = {
  startSchemaMonitoring: (pipelineId) => {
    const numericId = Number(pipelineId)
    if (!Number.isInteger(numericId)) {
      return Promise.reject(new Error('Invalid pipeline id: must be an integer'))
    }
    return api.post(`/api/v1/cdc/pipeline/${numericId}/schema-monitoring/start`)
  },
  stopSchemaMonitoring: (pipelineId) => {
    const numericId = Number(pipelineId)
    if (!Number.isInteger(numericId)) {
      return Promise.reject(new Error('Invalid pipeline id: must be an integer'))
    }
    return api.post(`/api/v1/cdc/pipeline/${numericId}/schema-monitoring/stop`)
  },
  getSchemaMonitoringStatus: (pipelineId) => {
    const numericId = Number(pipelineId)
    if (!Number.isInteger(numericId)) {
      return Promise.reject(new Error('Invalid pipeline id: must be an integer'))
    }
    return api.get(`/api/v1/cdc/pipeline/${numericId}/schema-monitoring/status`)
  },
  listKafkaTopics: () => api.get('/api/v1/cdc/kafka/topics'),
  getKafkaTopicInfo: (topicName) => api.get(`/api/v1/cdc/kafka/topics/${encodeURIComponent(topicName)}`)
}

export const pipelineStepAPI = {
  createStep: data => api.post('/api/v1/pipeline-steps/', data),
  updateStep: data => api.patch('/api/v1/pipeline-steps/', data),
  deleteStep: stepId => api.delete(`/api/v1/pipeline-steps/${stepId}`),
  getStepsByPipeline: pipelineId => api.get(`/api/v1/pipeline-steps/step/${pipelineId}`),
}

export const stepConfigurationAssociationAPI = {
  createAssociation: data => api.post('/api/v1/step-configuration-association/', data),
  getConfigsByStep: stepId => api.get(`/api/v1/step-configuration-association/step/${stepId}/configs`),
  getStepsByConfig: configId => api.get(`/api/v1/step-configuration-association/config/${configId}/steps`),
}

export const agenticTransformationAPI = {
  createTransformation: data => api.post('/api/v1/agentic-transformation/', data),
}
