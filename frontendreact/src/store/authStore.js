import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { userAPI } from '../api/userApi'
import toast from 'react-hot-toast'
import { decodeJWTToken } from '../utils/auth'
import { handleApiError } from '../utils/errorHandler'

const useAuthStore = create(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      loginStatus: 'loggedout',
      setUser: user => set({ user, isAuthenticated: !!user }),
      setToken: token => set({ token }),
      setLoginStatus: status => set({ loginStatus: status }),
      setLoading: loading => set({ isLoading: loading }),

      login: async credentials => {
        set({ isLoading: true })
        try {
          const response = await userAPI.login(credentials)
          const access_token = response.access_token

          const user = decodeJWTToken(access_token)

          localStorage.setItem('token', access_token)
          localStorage.setItem('user', JSON.stringify(user))
          localStorage.setItem('login_status', 'loggedin')

          set({
            user,
            token: access_token,
            isAuthenticated: true,
            loginStatus: 'loggedin',
            isLoading: false
          })

          toast.success('Login successful!')
          return { success: true, user }
        } catch (error) {
          set({ isLoading: false })
          return handleApiError(error, 'Login failed', toast.error)
        }
      },

      logout: async () => {
        set({ isLoading: true })

        localStorage.removeItem('token')
        localStorage.removeItem('user')
        localStorage.setItem('login_status', 'loggedout')

        set({
          user: null,
          token: null,
          isAuthenticated: false,
          loginStatus: 'loggedout',
          isLoading: false
        })

        toast.success('Logged out successfully')
      },

      checkAuth: async () => {
        const token = localStorage.getItem('token')
        const loginStatus = localStorage.getItem('login_status')

        if (token && loginStatus === 'loggedin') {
          try {
            const userData = decodeJWTToken(token)
            if (userData) {
              set({
                user: userData,
                token,
                isAuthenticated: true,
                loginStatus: 'loggedin'
              })
              return true
            } else {
              get().logout()
              return false
            }
          } catch (error) {
            get().logout()
            return false
          }
        } else {
          set({
            user: null,
            token: null,
            isAuthenticated: false,
            loginStatus: 'loggedout'
          })
          return false
        }
      },

      updateProfile: async profileData => {
        set({ isLoading: true })
        try {
          const response = await userAPI.updateProfile(profileData)
          const updatedUser = response.data

          set({ user: updatedUser, isLoading: false })
          localStorage.setItem('user', JSON.stringify(updatedUser))

          toast.success('Profile updated successfully!')
          return { success: true, user: updatedUser }
        } catch (error) {
          set({ isLoading: false })
          return handleApiError(error, 'Failed to update profile', toast.error)
        }
      },

      getCurrentUser: () => {
        return get().user
      },

      isAdmin: () => {
        const user = get().user
        const isAdminUser = user?.role === 'admin'
        return isAdminUser
      },

      clearAll: () => {
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          isLoading: false,
          loginStatus: 'loggedout'
        })
        localStorage.clear()
      }
    }),
    {
      name: 'auth-storage',
      partialize: state => ({
        user: state.user,
        token: state.token,
        loginStatus: state.loginStatus
      })
    }
  )
)

export default useAuthStore
