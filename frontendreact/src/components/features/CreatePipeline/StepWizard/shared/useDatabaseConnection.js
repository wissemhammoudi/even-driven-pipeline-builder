import { useState, useEffect, useCallback } from 'react'

export const useDatabaseConnection = (allPipelineSteps, stepType = 'ingestion') => {
  const [connectionConfig, setConnectionConfig] = useState({})
  const [isLoadingConnection, setIsLoadingConnection] = useState(false)
  const [connectionError, setConnectionError] = useState(null)
  const [sourceConfigDisplay, setSourceConfigDisplay] = useState(null)

  const extractDatabaseConfig = useCallback((allPipelineSteps) => {
    if (allPipelineSteps && typeof allPipelineSteps === 'object' && allPipelineSteps.step_config) {
      const stepConfig = allPipelineSteps.step_config
      
      let connConfig = {}
      
      if (stepConfig?.connection_config) {
        if (stepConfig.tool === 'dlt' && stepConfig.connection_config.source) {
          connConfig = stepConfig.connection_config.source
        } else if (stepConfig.tool === 'meltano' && stepConfig.connection_config.extractor) {
          connConfig = stepConfig.connection_config.extractor
        } else if (stepConfig.tool === 'sqlmesh' && stepConfig.connection_config.utility) {
          connConfig = stepConfig.connection_config.utility
        } else {
          connConfig = stepConfig.connection_config.source ||
                      stepConfig.connection_config.extractor ||
                      stepConfig.connection_config.utility ||
                      stepConfig.connection_config
        }
      } else if (stepConfig.connection) {
        connConfig = stepConfig.connection
      } else if (stepConfig.db) {
        connConfig = stepConfig.db
      } else {
        for (const [key, value] of Object.entries(stepConfig)) {
          if (
            value &&
            typeof value === 'object' &&
            (value.host || value.dbname || value.database) &&
            (value.user || value.username) &&
            value.password
          ) {
            connConfig = value
            break
          }
        }
      }
      
      const hasHost = connConfig.host && String(connConfig.host).trim() !== ''
      const hasDatabase = (connConfig.database || connConfig.dbname) && String(connConfig.database || connConfig.dbname).trim() !== ''
      const hasUser = (connConfig.user || connConfig.username) && String(connConfig.user || connConfig.username).trim() !== ''
      const hasPassword = connConfig.password && String(connConfig.password).trim() !== ''

      if (hasHost && hasDatabase && hasUser && hasPassword) {
        return {
          host: connConfig.host || '',
          port: parseInt(connConfig.port) || 5432,
          database: connConfig.database || connConfig.dbname || '',
          user: connConfig.user || connConfig.username || '',
          password: connConfig.password || '',
          schema: connConfig.schema || 'public'
        }
      }
    }

    const ingestionStep = allPipelineSteps?.find(
      step =>
        step.type === 'data ingestion' ||
        step.step_type === 'data_ingestion' ||
        step.step_type === 'ingestion' ||
        step.step_type === 'source'
    )

    const transformationStep = allPipelineSteps?.find(
      step =>
        step.type === 'data transformation' ||
        step.step_type === 'data_transformation' ||
        step.step_type === 'transformation'
    )

    let connConfig = {}

    if (stepType === 'ingestion' && ingestionStep?.step_config) {
      const stepConfig = ingestionStep.step_config

      if (stepConfig?.connection_config) {
        if (stepConfig.tool === 'dlt' && stepConfig.connection_config.source) {
          connConfig = stepConfig.connection_config.source
        } else if (
          stepConfig.tool === 'meltano' &&
          stepConfig.connection_config.extractor
        ) {
          connConfig = stepConfig.connection_config.extractor
        } else if (
          stepConfig.tool === 'sqlmesh' &&
          stepConfig.connection_config.utility
        ) {
          connConfig = stepConfig.connection_config.utility
        } else {
          connConfig =
            stepConfig.connection_config.source ||
            stepConfig.connection_config.extractor ||
            stepConfig.connection_config.utility ||
            stepConfig.connection_config
        }
      } else if (stepConfig.connection) {
        connConfig = stepConfig.connection
      } else if (stepConfig.db) {
        connConfig = stepConfig.db
      } else {
        for (const [key, value] of Object.entries(stepConfig)) {
          if (
            value &&
            typeof value === 'object' &&
            (value.host || value.dbname || value.database) &&
            (value.user || value.username) &&
            value.password
          ) {
            connConfig = value
            break
          }
        }
      }
    }

    if (stepType === 'transformation') {
      if (ingestionStep?.step_config) {
        const stepConfig = ingestionStep.step_config

        if (stepConfig?.connection_config) {
          if (stepConfig.tool === 'dlt' && stepConfig.connection_config.source) {
            connConfig = stepConfig.connection_config.source
          } else if (
            stepConfig.tool === 'meltano' &&
            stepConfig.connection_config.extractor
          ) {
            connConfig = stepConfig.connection_config.extractor
          } else if (
            stepConfig.tool === 'sqlmesh' &&
            stepConfig.connection_config.utility
          ) {
            connConfig = stepConfig.connection_config.utility
          } else {
            connConfig =
              stepConfig.connection_config.source ||
              stepConfig.connection_config.extractor ||
              stepConfig.connection_config.utility ||
              stepConfig.connection_config
          }
        }
      }

      if (
        !connConfig.host &&
        !connConfig.dbname &&
        !connConfig.database &&
        transformationStep?.step_config?.destination_config
      ) {
        const destConfig = transformationStep.step_config.destination_config

        if (
          destConfig.host &&
          (destConfig.database || destConfig.dbname) &&
          (destConfig.user || destConfig.username) &&
          destConfig.password
        ) {
          connConfig = {
            host: destConfig.host,
            port: destConfig.port || 5432,
            database: destConfig.database || destConfig.dbname,
            user: destConfig.user || destConfig.username,
            password: destConfig.password,
            schema: destConfig.schema || 'public'
          }
        }
      }
    }

    const hasHost = connConfig.host && String(connConfig.host).trim() !== ''
    const hasDatabase =
      (connConfig.database || connConfig.dbname) &&
      String(connConfig.database || connConfig.dbname).trim() !== ''
    const hasUser =
      (connConfig.user || connConfig.username) &&
      String(connConfig.user || connConfig.username).trim() !== ''
    const hasPassword =
      connConfig.password && String(connConfig.password).trim() !== ''

    if (!hasHost || !hasDatabase || !hasUser || !hasPassword) {
      return null
    }

    const finalConfig = {
      host: connConfig.host || '',
      port: parseInt(connConfig.port) || 5432,
      database: connConfig.database || connConfig.dbname || '',
      user: connConfig.user || connConfig.username || '',
      password: connConfig.password || '',
      schema: connConfig.schema || 'public'
    }

    return finalConfig
  }, [stepType])

  const loadConnectionConfig = useCallback(async () => {
    setIsLoadingConnection(true)
    setConnectionError(null)

    try {
      const config = extractDatabaseConfig(allPipelineSteps)

      if (!config) {
        setConnectionError(
          `No valid ${stepType} database configuration found. Please configure the database connection.`
        )
        setIsLoadingConnection(false)
        return
      }

      setConnectionConfig(config)
      setSourceConfigDisplay({
        ...config,
        source: stepType === 'ingestion' ? 'ingestion_step' : 'transformation_step'
      })
    } catch (error) {
      setConnectionError(
        error.response?.data?.message || 
        error.message || 
        'Failed to load connection configuration.'
      )
    } finally {
      setIsLoadingConnection(false)
    }
  }, [allPipelineSteps, extractDatabaseConfig, stepType])

  useEffect(() => {
    if (allPipelineSteps) {
      loadConnectionConfig()
    }
  }, [allPipelineSteps, loadConnectionConfig])

  return {
    connectionConfig,
    isLoadingConnection,
    connectionError,
    sourceConfigDisplay,
    loadConnectionConfig,
    extractDatabaseConfig
  }
} 