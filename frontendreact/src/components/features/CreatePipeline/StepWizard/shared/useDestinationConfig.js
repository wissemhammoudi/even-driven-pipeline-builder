import { useMemo } from 'react'

export const useDestinationConfig = (allPipelineSteps) => {
  const destinationConfig = useMemo(() => {
    if (!Array.isArray(allPipelineSteps)) {
      return null
    }

    const transformationStep = allPipelineSteps?.find(
      step => step?.type === 'data transformation'
    )

    const ingestionStep = allPipelineSteps?.find(
      step => step?.type === 'data ingestion'
    )

    const getTransformationDestinationConfig = () => {
      if (!transformationStep?.step_config?.destination_config) {
        return null
      }

      const destConfig = transformationStep.step_config.destination_config

      if (!destConfig || typeof destConfig !== 'object') {
        return null
      }

      if (destConfig.host && (destConfig.database || destConfig.dbname)) {
        return {
          host: String(destConfig.host),
          port: Number(destConfig.port) || 5432,
          database: String(destConfig.database || destConfig.dbname),
          user: String(destConfig.user || destConfig.username || ''),
          password: String(destConfig.password || ''),
          schema: String(destConfig.schema || 'public'),
          source: 'transformation',
          tool: String(transformationStep.step_config?.tool || '')
        }
      }

      return null
    }

    const getIngestionDestinationConfig = () => {
      if (!ingestionStep?.step_config?.connection_config) {
        return null
      }

      const connectionConfig = ingestionStep.step_config.connection_config

      if (!connectionConfig || typeof connectionConfig !== 'object') {
        return null
      }

      let destConfig = null
      const ingestionTool = String(ingestionStep.step_config?.tool || '')

      if (ingestionTool === 'meltano') {
        destConfig = connectionConfig.loader
      } else if (ingestionTool === 'dlt') {
        destConfig = connectionConfig.destination
      } else {
        destConfig = connectionConfig.loader || connectionConfig.destination
      }

      if (!destConfig || typeof destConfig !== 'object' || !destConfig.host) {
        return null
      }

      return {
        host: String(destConfig.host),
        port: Number(destConfig.port) || 5432,
        database: String(destConfig.database || destConfig.dbname || ''),
        user: String(destConfig.user || destConfig.username || ''),
        password: String(destConfig.password || ''),
        schema: String(destConfig.schema || destConfig.target_schema || 'public'),
        source: 'ingestion',
        tool: ingestionTool
      }
    }

    const transformationDestConfig = getTransformationDestinationConfig()
    const ingestionDestConfig = getIngestionDestinationConfig()

    return transformationDestConfig || ingestionDestConfig
  }, [allPipelineSteps])

  const canUseExistingConnection = Boolean(destinationConfig && destinationConfig.host)

  return {
    destinationConfig,
    canUseExistingConnection
  }
} 