import { create } from 'zustand'
import { toast } from 'react-hot-toast'
import dashboardApi from '../api/dashboardApi'

const useDashboardStore = create((set, get) => ({
  dashboardData: {
    stats: {
      pipelines: { total: 0, active: 0, deprecated: 0 },
      runs: {
        total: 0,
        successful: 0,
        failed: 0,
        success_rate: 0,
        avg_duration_minutes: 0
      }
    },
    charts: {
      pipeline_creation_trend: [],
      duration_distribution: [],
      pipeline_status_distribution: [],
      success_failure_distribution: [],
      days_filter: 30
    },
    recent_pipelines: []
  },
  isLoading: false,
  isRefreshing: false,
  error: null,
  lastFetchedUserId: null,
  lastFetchedAt: null,
  
  loadDashboardData: async (userId, forceRefresh = false) => {
    const { lastFetchedUserId, lastFetchedAt } = get()
    
    const isStale = lastFetchedAt && (Date.now() - lastFetchedAt) > 5 * 60 * 1000
    const shouldFetch = forceRefresh || userId !== lastFetchedUserId || !lastFetchedAt || isStale

    if (!shouldFetch) {
      return
    }

    try {
      if (forceRefresh) {
        set({ isRefreshing: true, error: null })
      } else {
        set({ isLoading: true, error: null })
      }

      const apiResponse = await dashboardApi.getDashboardData(userId)

      const combinedData = {
        stats: apiResponse.stats || {
          pipelines: { total: 0, active: 0, deprecated: 0 },
          runs: {
            total: 0,
            successful: 0,
            failed: 0,
            success_rate: 0,
            avg_duration_minutes: 0
          }
        },
        charts: {
          pipeline_creation_trend: apiResponse.charts?.pipeline_creation_trend || [],
          pipeline_status_distribution: apiResponse.charts?.pipeline_status_distribution || [],
          success_failure_distribution: apiResponse.charts?.success_failure_distribution || [],
          duration_distribution: [],
          days_filter: apiResponse.charts?.days_filter || 30
        },
        recent_pipelines: apiResponse.recent_pipelines || []
      }
      
      set({ 
        dashboardData: combinedData,
        lastFetchedUserId: userId,
        lastFetchedAt: Date.now(),
        error: null
      })
    } catch (err) {
      const errorMessage = err.message || 'Failed to load dashboard data'
      set({ error: errorMessage })

      if (forceRefresh) {
        toast.error('Failed to refresh dashboard data')
      }
    } finally {
      set({ isLoading: false, isRefreshing: false })
    }
  },

  refreshData: async (userId) => {
    await get().loadDashboardData(userId, true)
  },

  clearError: () => {
    set({ error: null })
  },

  reset: () => {
    set({
      dashboardData: {
        stats: {
          pipelines: { total: 0, active: 0, deprecated: 0 },
          runs: {
            total: 0,
            successful: 0,
            failed: 0,
            success_rate: 0,
            avg_duration_minutes: 0
          }
        },
        charts: {
          pipeline_creation_trend: [],
          duration_distribution: [],
          pipeline_status_distribution: [],
          run_success_failure_trend: [],
          days_filter: 30
        },
        recent_pipelines: []
      },
      isLoading: false,
      isRefreshing: false,
      error: null,
      lastFetchedUserId: null,
      lastFetchedAt: null
    })
  }
}))

export default useDashboardStore 
