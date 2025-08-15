import { create } from 'zustand'
import { toast } from 'react-hot-toast'
import { pipelineAPI } from '../api/pipelineApi'
import { pipelineRunAPI } from '../api/pipelineRunApi'
import userPipelineAccessAPI from '../api/userPipelineAccessApi'
import { pipelineAPI as pipelineApiFunctions } from '../utils/api'
import { handleApiError } from '../utils/errorHandler'

const usePipelineStore = create((set, get) => ({
  pipelines: [],
  totalCount: 0,
  currentPage: 1,
  pageSize: 10,
  isLoading: false,
  error: null,

  currentPipeline: null,
  currentPipelineSteps: [],
  currentPipelineRuns: [],
  isLoadingPipeline: true,
  permissions: {
    loading: true,
    can_view_pipeline: false,
    can_edit_pipeline: false,
    can_start_pipeline: false,
    can_start_visualization: false,
    can_delete_pipeline: false,
    can_manage_access: false
  },

  isRunning: false,
  isVisualizationRunning: false,
  visualizationUrl: null,
  visualizationCreds: null,

  pipelineSteps: [],

  fetchPipelines: async (userId, filters = {}) => {
    set({ isLoading: true, error: null })
    try {
      const params = {
        user_id: userId,
        deprecated: filters.deprecated || false,
        page: filters.page || 1,
        page_size: filters.page_size || 10,
        name: filters.name,
        created_date: filters.created_date
      }

      const responseData = await pipelineAPI.getPipelines(userId,params)
      const pipelines = Array.isArray(responseData.data) ? responseData.data : [];
      set({ 
        pipelines,
        totalCount: responseData.total || 0,
        currentPage: Math.floor((responseData.offset || 0) / (responseData.limit || 10)) + 1,
        pageSize: responseData.limit || 10
      })

      return { success: true, data: pipelines }
    } catch (error) {
      const result = handleApiError(error, 'Failed to fetch pipelines', toast.error)
      set({ error: result.error })
      return result
    } finally {
      set({ isLoading: false })
    }
  },

  createPipeline: async pipelineData => {
    set({ isLoading: true, error: null })
    try {
      const responseData = await pipelineAPI.createPipeline(pipelineData)
      toast.success('Pipeline created successfully!')
      
      const user = JSON.parse(localStorage.getItem('user') || '{}')
      if (user && user.user_id) {
        await get().fetchPipelines(parseInt(user.user_id, 10), { deprecated: false, page: 1, page_size: 10 })
      } else {
        console.warn('createPipeline: user_id is undefined, not fetching pipelines')
      }
      return { success: true, data: responseData }
    } catch (error) {
      const result = handleApiError(error, 'Failed to create pipeline', toast.error)
      set({ error: result.error })
      return result
    } finally {
      set({ isLoading: false })
    }
  },

  deletePipeline: async (pipelineId) => {
    try {
      const responseData = await pipelineAPI.deletePipeline(pipelineId)
      toast.success('Pipeline deleted successfully!')
      return { success: true, data: responseData }
    } catch (error) {
      return handleApiError(error, 'Failed to delete pipeline', toast.error)
    }
  },

  loadPipelineData: async (pipelineId, user) => {
    set({ isLoadingPipeline: true, error: null })
    
    try {
      if (!user?.user_id) {
        throw new Error('User not authenticated')
      }

      let pipelineData
      try {
        const response = await pipelineAPI.getPipelineById(pipelineId)
        pipelineData = response.data || response
      } catch (pipelineError) {
        if (user.role === 'admin') {
          const allPipelines = await pipelineAPI.getPipelines()
          pipelineData = allPipelines.find(p => p.pipeline_id === parseInt(pipelineId))
          if (!pipelineData) throw new Error('Pipeline not found')
        } else {
          throw pipelineError
        }
      }

      const [stepsResult, runsResult] = await Promise.allSettled([
        pipelineApiFunctions.getPipelineStepsDetails(pipelineId),
        pipelineRunAPI.getPipelineRunsByPipelineId(pipelineId)
      ])

      set({
        currentPipeline: pipelineData,
        currentPipelineSteps: stepsResult.status === 'fulfilled' ? stepsResult.value.data : [],
        currentPipelineRuns: runsResult.status === 'fulfilled' ? runsResult.value : []
      })

      return { success: true }
    } catch (error) {
      const result = handleApiError(error, 'Failed to load pipeline data')
      set({ error: result.error })
      return result
    } finally {
      set({ isLoadingPipeline: false })
    }
  },

  loadPermissions: async (pipelineId, userId) => {
    if (!pipelineId || !userId) {
      set({ permissions: { ...get().permissions, loading: false } })
      return
    }

    try {
      const response = await userPipelineAccessAPI.getUserPermissions(pipelineId, userId)
      set({
        permissions: {
          loading: false,
          can_view_pipeline: response.can_view_pipeline || false,
          can_edit_pipeline: response.can_edit_pipeline || false,
          can_start_pipeline: response.can_start_pipeline || false,
          can_start_visualization: response.can_start_visualization || false,
          can_delete_pipeline: response.can_delete_pipeline || false,
          can_manage_access: response.can_manage_access || false
        }
      })
    } catch (error) {
      set({
        permissions: {
          loading: false,
          can_view_pipeline: false,
          can_edit_pipeline: false,
          can_start_pipeline: false,
          can_start_visualization: false,
          can_delete_pipeline: false,
          can_manage_access: false
        }
      })
    }
  },

  runPipeline: async (pipelineId, userId) => {
    set({ isRunning: true })
    const loadingToast = toast.loading('Starting pipeline...', { duration: Infinity })

    try {
      await pipelineRunAPI.startPipeline(parseInt(pipelineId), parseInt(userId))
      toast.dismiss(loadingToast)
      toast.success('Pipeline started successfully!')
        
      const runs = await pipelineRunAPI.getPipelineRunsByPipelineId(pipelineId)
      set({ currentPipelineRuns: runs })
      
      return { success: true }
    } catch (error) {
      toast.dismiss(loadingToast)
      toast.error('Failed to start pipeline')
      return { success: false }
    } finally {
      set({ isRunning: false })
    }
  },

  startVisualization: async (pipelineId, userId) => {
    set({ isVisualizationRunning: true })
    
    try {
      const responseData = await pipelineRunAPI.startVisualization(pipelineId, userId)
      
      if (responseData?.visualization_url) {
        set({
          visualizationUrl: responseData.visualization_url,
          visualizationCreds: {
            username: responseData.username,
            password: responseData.password
          }
        })
        toast.success('Visualization started successfully!')
        return { success: true }
      } else {
        toast.error('Failed to start visualization')
        return { success: false }
      }
    } catch (error) {
      toast.error('Failed to start visualization')
      return { success: false }
    } finally {
      set({ isVisualizationRunning: false })
    }
  },

  stopVisualization: () => {
    set({ visualizationUrl: null, visualizationCreds: null })
    toast.success('Visualization stopped successfully!')
  },

  resetCurrentPipeline: () => {
    set({
      currentPipeline: null,
      currentPipelineSteps: [],
      currentPipelineRuns: [],
      isLoadingPipeline: true,
      permissions: {
        loading: true,
        can_view_pipeline: false,
        can_edit_pipeline: false,
        can_start_pipeline: false,
        can_start_visualization: false,
        can_delete_pipeline: false,
        can_manage_access: false
      },
      isRunning: false,
      isVisualizationRunning: false,
      visualizationUrl: null,
      visualizationCreds: null
    })
  },

  addPipelineStep: (step) => {
    set((state) => ({
      pipelineSteps: [...(Array.isArray(state.pipelineSteps) ? state.pipelineSteps : []), step]
    }))
  },

  updatePipelineStep: (index, step) => {
    set((state) => ({
      pipelineSteps: (Array.isArray(state.pipelineSteps) ? state.pipelineSteps : []).map((s, i) => i === index ? step : s)
    }))
  },

  removePipelineStep: (index) => {
    set((state) => ({
      pipelineSteps: (Array.isArray(state.pipelineSteps) ? state.pipelineSteps : []).filter((_, i) => i !== index)
    }))
  },

  clearPipelineSteps: () => {
    set({ pipelineSteps: [] })
  }
}))
export default usePipelineStore 
