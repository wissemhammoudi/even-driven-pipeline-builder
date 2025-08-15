import { useState, useEffect, useCallback } from 'react'
import { pipelineAPI } from '../../../../../api/pipelineApi'

export const useSchemaInfo = (connectionConfig) => {
  const [schemaInfo, setSchemaInfo] = useState({})
  const [isLoadingSchema, setIsLoadingSchema] = useState(false)
  const [schemaError, setSchemaError] = useState(null)

  const fetchSchemaInfo = useCallback(async () => {
    if (!connectionConfig || !connectionConfig.host) {
      setSchemaError('No valid connection configuration provided')
      return
    }

    setIsLoadingSchema(true)
    setSchemaError(null)

    try {
      const apiPayload = {
        host: connectionConfig.host,
        dbname: connectionConfig.database || connectionConfig.dbname,
        user: connectionConfig.user,
        password: connectionConfig.password,
        port: connectionConfig.port || 5432,
        schema: connectionConfig.schema || 'public'
      }
      const response = await pipelineAPI.getDatabaseSchema(apiPayload)
      if (response && Object.keys(response).length > 0) {
        setSchemaInfo(response)
      } else {
        setSchemaError('No tables found in the database schema.')
      }
    } catch (error) {
      setSchemaError(
        error.response?.data?.message || 
        error.message || 
        'Failed to fetch schema information. Please check your connection settings.'
      )
    } finally {
      setIsLoadingSchema(false)
    }
  }, [connectionConfig])

  const getAllTables = useCallback(() => {
    const tables = []
    Object.entries(schemaInfo).forEach(([schemaName, schemaTables]) => {
      Object.entries(schemaTables).forEach(([tableName, columns]) => {
        tables.push({
          name: tableName,
          schema: schemaName,
          columns: columns
        })
      })
    })
    return tables
  }, [schemaInfo])

  const getTableColumns = useCallback((tableName) => {
    for (const [schema, schemaTables] of Object.entries(schemaInfo)) {
      if (schemaTables[tableName]) return schemaTables[tableName]
    }
    return []
  }, [schemaInfo])

  const getSchemaName = useCallback((sourceConn) => {
    return sourceConn.filter_schema || 
           (Array.isArray(sourceConn.filter_schemas) ? sourceConn.filter_schemas[0] : sourceConn.filter_schemas) ||
           sourceConn.schema || 
           sourceConn.default_target_schema || 
           'public'
  }, [])

  useEffect(() => {
    if (connectionConfig && connectionConfig.host) {
      fetchSchemaInfo()
    }
  }, [connectionConfig, fetchSchemaInfo])

  return {
    schemaInfo,
    isLoadingSchema,
    schemaError,
    getAllTables,
    getTableColumns,
    getSchemaName,
    fetchSchemaInfo
  }
} 