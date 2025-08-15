import React, { useEffect } from 'react'
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate
} from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import Layout from './components/common/Layout/Layout'
import LoginPage from './pages/LoginPage/LoginPage'
import Dashboard from './pages/Dashboard/Dashboard'
import ProfilePage from './pages/UpdateProfilePage/UpdateProfilePage'
import useAuthStore from './store/authStore'
import ConfigManagementPage from './pages/ConfigManagementPage/ConfigManagementPage'
import ViewPipelinePage from './pages/ViewPipelinePage/ViewPipelinePage'
import PipelineManagementPage from './pages/PipelineManagementPage/PipelineManagementPage'
import CreatePipelinePage from './pages/CreatePipelinePage/CreatePipelinePage'
import './index.css'  

const ProtectedRoute = ({ children }) => {
  const { user } = useAuthStore()
  return user ? children : <Navigate to='/login' replace />
}

function App () {
  const { checkAuth } = useAuthStore()

  useEffect(() => {
    checkAuth()
  }, [checkAuth])
  return (
    <Router>
      <div className='App'>
        <Toaster
          position='top-right'
          toastOptions={{
            duration: 4000,
            style: {
              background: '#ffffff',
              color: '#374151',
              border: '1px solid #e5e7eb',
              boxShadow:
                '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)'
            },
            success: {
              duration: 3000,
              iconTheme: {
                primary: '#05BAEE',
                secondary: '#ffffff'
              },
              style: {
                background: '#ffffff',
                color: '#374151',
                border: '1px solid #d1fae5'
              }
            },
            error: {
              duration: 5000,
              iconTheme: {
                primary: '#D6007F',
                secondary: '#ffffff'
              },
              style: {
                background: '#ffffff',
                color: '#374151',
                border: '1px solid #fecaca'
              }
            }
          }}
        />

        <Routes>
          <Route path='/login' element={<LoginPage />} />

          <Route
            path='/'
            element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to='/dashboard' replace />} />
            <Route path='dashboard' element={<Dashboard />} />
            <Route path='view-pipeline/:pipelineId' element={<ViewPipelinePage />}/>
            <Route path='profile' element={<ProfilePage />} />
            <Route path='config-management' element={<ConfigManagementPage />} />
            <Route path='pipeline-management' element={<PipelineManagementPage />} />
            <Route path='create-pipeline' element={<CreatePipelinePage />} />
          </Route>
          <Route path='*' element={<Navigate to='/dashboard' replace />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App