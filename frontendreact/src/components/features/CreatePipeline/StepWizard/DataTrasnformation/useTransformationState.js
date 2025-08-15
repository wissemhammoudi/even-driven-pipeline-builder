import { useState, useCallback, useMemo, useRef } from 'react'

export const useTransformationState = (formData, onInputChange, tableConfig = {}) => {
  const initializedRef = useRef(false)
  const lastFormDataRef = useRef(null)
  const updateTimeoutRef = useRef(null)
  
  const currentFormData = useMemo(() => ({
    columnFunctions: formData.step_config?.column_functions?.tables || {},
    joinTransformations: formData.step_config?.join_transformations || [],
    agenticTransformations: formData.step_config?.agentic_transformations || []
  }), [formData.step_config])

  const [columnFunctions, setColumnFunctions] = useState(currentFormData.columnFunctions)
  const [joinTransformations, setJoinTransformations] = useState(currentFormData.joinTransformations)
  const [agenticTransformations, setAgenticTransformations] = useState(currentFormData.agenticTransformations)

  const formDataChanged = useMemo(() => {
    const lastData = lastFormDataRef.current
    const currentData = currentFormData
    
    if (!lastData) {
      lastFormDataRef.current = currentData
      return false
    }
    
    const changed = JSON.stringify(lastData) !== JSON.stringify(currentData)
    if (changed) {
      lastFormDataRef.current = currentData
    }
    return changed
  }, [currentFormData])

  if (formDataChanged && !initializedRef.current) {
    setColumnFunctions(currentFormData.columnFunctions)
    setJoinTransformations(currentFormData.joinTransformations)
    setAgenticTransformations(currentFormData.agenticTransformations)
    initializedRef.current = true
  }

  const batchedUpdate = useCallback((updater) => {
    if (updateTimeoutRef.current) {
      clearTimeout(updateTimeoutRef.current)
    }
    
    updateTimeoutRef.current = setTimeout(() => {
      updater()
      updateTimeoutRef.current = null
    }, 0)
  }, [])

  const stableOnInputChange = useCallback((field, value) => {
    batchedUpdate(() => {
      onInputChange(field, value)
    })
  }, [onInputChange, batchedUpdate])

  const handleColumnFunctionChange = useCallback((tableName, columnName, functionName) => {
    
    setColumnFunctions(prev => {
      const newFunctions = {
        ...prev,
        [tableName]: {
          ...prev[tableName],
          [columnName]: functionName
        }
      }
      
      const updatedStepConfig = {
        ...formData.step_config,
        column_functions: {
          tables: newFunctions
        }
      }
      
      stableOnInputChange('step_config', updatedStepConfig)
      return newFunctions
    })
  }, [formData.step_config, stableOnInputChange])
  
  const updateTableSyncConfig = useCallback(() => {
    
    const tables = Object.keys(tableConfig).map(table => {
      const tableColumns = tableConfig[table] || []
      const columnNames = tableColumns
        .map(col => col.column_name || col.column || col.name)
        .filter(Boolean)
      
      return {
        schema_name: 'public',
        table_name: table,
        pk: ['id'],
        incremental_col: 'id',
        columns: columnNames.join(',')
      }
    }).filter(table => table.columns.length > 0)
    
    const updatedStepConfig = {
      ...formData.step_config,
      table_sync_config: { tables }
    }
    
    stableOnInputChange('step_config', updatedStepConfig)
  }, [formData.step_config, tableConfig, stableOnInputChange])

  const handleAddJoinTransformation = useCallback((joinConfig) => {
    setJoinTransformations(prev => {
      const newJoins = [...prev, joinConfig]
      
      stableOnInputChange('step_config', {
        ...formData.step_config,
        join_transformations: newJoins
      })
      
      return newJoins
    })
  }, [formData.step_config, stableOnInputChange])

  const handleRemoveJoinTransformation = useCallback((index) => {
    setJoinTransformations(prev => {
      const newJoins = prev.filter((_, i) => i !== index)
      
      stableOnInputChange('step_config', {
        ...formData.step_config,
        join_transformations: newJoins
      })
      
      return newJoins
    })
  }, [formData.step_config, stableOnInputChange])

  const handleClearAllJoins = useCallback(() => {
    setJoinTransformations([])
    
    stableOnInputChange('step_config', {
      ...formData.step_config,
      join_transformations: []
    })
  }, [formData.step_config, stableOnInputChange])
  
  const handleAddAgenticTransformation = useCallback((transformation) => {
    setAgenticTransformations(prev => {
      const newTransformations = [...prev, transformation]
      
      stableOnInputChange('step_config', {
        ...formData.step_config,
        agentic_transformations: newTransformations
      })
      
      return newTransformations
    })
  }, [formData.step_config, stableOnInputChange])

  const handleRemoveAgenticTransformation = useCallback((index) => {
    setAgenticTransformations(prev => {
      const newTransformations = prev.filter((_, i) => i !== index)
        
      stableOnInputChange('step_config', {
        ...formData.step_config,
        agentic_transformations: newTransformations
      })
      
      return newTransformations
    })
  }, [formData.step_config, stableOnInputChange])

  return {
    columnFunctions,
    joinTransformations,
    agenticTransformations,
    handleColumnFunctionChange,
    updateTableSyncConfig,
    handleAddJoinTransformation,
    handleRemoveJoinTransformation,
    handleClearAllJoins,
    handleAddAgenticTransformation,
    handleRemoveAgenticTransformation
  }
} 