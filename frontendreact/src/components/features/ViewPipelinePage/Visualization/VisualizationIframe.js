import React, { useEffect, useState } from 'react'

const VisualizationIframe = ({ visualizationUrl, onRefresh }) => {
  const [iframeLoaded, setIframeLoaded] = useState(false)
  const [iframeError, setIframeError] = useState(false)
  
  const handleIframeLoad = () => {
    setIframeLoaded(true)
    setIframeError(false)
    const loadingElement = document.getElementById('iframe-loading')
    if (loadingElement) {
      loadingElement.style.display = 'none'
    }
  }

  const handleIframeError = () => {
    setIframeError(true)
    setIframeLoaded(false)
    const loadingElement = document.getElementById('iframe-loading')
    if (loadingElement) {
      loadingElement.innerHTML = `
        <div class="text-center">
          <div class="text-red-500 mb-4">
            <svg class="h-12 w-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
            </svg>
          </div>
          <p class="text-gray-600 mb-4">Failed to load visualization in iframe</p>
          <p class="text-gray-500 text-sm mb-4">This might be due to authentication or security restrictions.</p>
          <a 
            href="${visualizationUrl}" 
            target="_blank" 
            rel="noopener noreferrer"
            class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
          >
            <svg class="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>
            </svg>
            Open in New Tab
          </a>
        </div>
      `
    }
  }

  const handleRefresh = () => {
    if (onRefresh) {
      const iframe = document.querySelector('iframe[title="Superset Visualization"]')
      if (iframe) {
        const currentSrc = iframe.src
        iframe.src = 'about:blank'
        setTimeout(() => {
          iframe.src = currentSrc
        }, 100)
        const loadingElement = document.getElementById('iframe-loading')
        if (loadingElement) {
          loadingElement.style.display = 'flex'
          loadingElement.innerHTML = `
            <div class="text-center">
              <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
              <p class="text-gray-600">Refreshing Superset visualization...</p>
            </div>
          `
        }
      }
    }
  }

  useEffect(() => {
    if (visualizationUrl) {
      setIframeLoaded(false)
      setIframeError(false)
      const loadingElement = document.getElementById('iframe-loading')
      if (loadingElement) {
        loadingElement.style.display = 'flex'
        loadingElement.innerHTML = `
          <div class="text-center">
            <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
            <p class="text-gray-600">Loading Superset visualization...</p>
          </div>
        `
      }
    }
  }, [visualizationUrl])

  if (!visualizationUrl) {
    return (
      <div className="flex items-center justify-center h-full bg-gray-100">
        <div className="text-center">
          <div className="text-gray-500 mb-4">
            <svg className="h-12 w-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
            </svg>
          </div>
          <p className="text-gray-600">No visualization URL provided</p>
        </div>
      </div>
    )
  }

  return (
    <div className='w-full h-full relative' style={{ height: 'calc(100vh - 250px)' }}>
      <iframe
        src={visualizationUrl}
        title='Superset Visualization'
        className='w-full h-full border-0 bg-white'
        sandbox='allow-same-origin allow-scripts allow-forms allow-popups allow-popups-to-escape-sandbox allow-presentation allow-top-navigation allow-top-navigation-by-user-activation'
        loading='lazy'
        onLoad={handleIframeLoad}
        onError={handleIframeError}
        style={{ minHeight: '600px' }}
        allow="fullscreen"
        referrerPolicy="no-referrer"
      />
      
      <div
        className='absolute inset-0 flex items-center justify-center bg-gray-100 z-10'
        id='iframe-loading'
      >
        <div className='text-center'>
          <div className='animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4'></div>
          <p className='text-gray-600'>Loading Superset visualization...</p>
        </div>
      </div>
    </div>
  )
}

export default VisualizationIframe 