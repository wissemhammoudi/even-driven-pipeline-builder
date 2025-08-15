import { useState } from 'react'

export function useJoinTransformation(tableConfig) {
  const [step, setStep] = useState(1)
  const [primaryTable, setPrimaryTable] = useState('')
  const [modelName, setModelName] = useState('')
  const [selectedTargetTables, setSelectedTargetTables] = useState([])
  const [tableConfigs, setTableConfigs] = useState({})

  const getTableColumns = (tableName) => {
    const tableSchema = tableConfig[tableName]
    if (tableSchema && Array.isArray(tableSchema)) {
      return tableSchema.map(col => col.column || col.column_name || col.name || '')
    }
    return []
  }

  const handlePrimaryTableSelect = () => {
    if (primaryTable && modelName.trim()) {
      setStep(2)
    }
  }

  const handleTargetTableToggle = (tableName) => {
    setSelectedTargetTables(prev => {
      if (prev.includes(tableName)) {
        return prev.filter(name => name !== tableName)
      } else {
        return [...prev, tableName]
      }
    })
  }

  const handleTargetTablesConfirm = () => {
    if (selectedTargetTables.length > 0) {
      setStep(3)
    }
  }

  const handleTableConfigChange = (tableName, field, value) => {
    setTableConfigs(prev => ({
      ...prev,
      [tableName]: {
        ...prev[tableName],
        [field]: value
      }
    }))
  }

  const handleColumnToggle = (tableName, columnName) => {
    const currentColumns = tableConfigs[tableName]?.selectedColumns || []
    const newColumns = currentColumns.includes(columnName) 
      ? currentColumns.filter(col => col !== columnName)
      : [...currentColumns, columnName]
    
    handleTableConfigChange(tableName, 'selectedColumns', newColumns)
  }

  const handleBack = () => {
    if (step === 2) {
      setStep(1)
      setSelectedTargetTables([])
    } else if (step === 3) {
      setStep(2)
      setTableConfigs({})
    }
  }

  const handleReset = () => {
    setStep(1)
    setPrimaryTable('')
    setModelName('')
    setSelectedTargetTables([])
    setTableConfigs({})
  }

  const isStepComplete = () => {
    if (step === 1) return primaryTable && modelName.trim()
    if (step === 2) return selectedTargetTables.length > 0
    if (step === 3) {
      return selectedTargetTables.every(table => {
        const config = tableConfigs[table]
        return config && config.joinType && config.condition && config.selectedColumns && config.selectedColumns.length > 0
      })
    }
    return false
  }

  const buildJoinTransformation = () => {
    if (!primaryTable || selectedTargetTables.length === 0) return null

    const targetTablesConfig = selectedTargetTables.map(targetTable => {
      const config = tableConfigs[targetTable]
      if (!config || !config.condition || !config.selectedColumns || config.selectedColumns.length === 0) {
        return null
      }

      const [sourceCol, targetCol] = config.condition.split(' = ')
      const sourceColumn = sourceCol?.split('.')[1] || ''
      const targetColumn = targetCol?.split('.')[1] || ''

      return {
        target_table: targetTable,
        join_type: config.joinType || 'INNER',
        join_conditions: [
          {
            source_column: sourceColumn,
            target_column: targetColumn
          }
        ],
        columns: config.selectedColumns
      }
    }).filter(Boolean)

    if (targetTablesConfig.length === 0) return null

    const primaryTableColumns = getTableColumns(primaryTable)

    return {
      primary_table: primaryTable,
      target_tables: targetTablesConfig,
      primary_table_columns: primaryTableColumns,
      name: modelName.trim() || `${primaryTable}_${selectedTargetTables.join('_')}_join`
    }
  }

  const resetForm = () => {
    handleReset()
  }

  return {
    step,
    primaryTable,
    setPrimaryTable,
    modelName,
    setModelName,
    selectedTargetTables,
    tableConfigs,
    getTableColumns,
    handlePrimaryTableSelect,
    handleTargetTableToggle,
    handleTargetTablesConfirm,
    handleTableConfigChange,
    handleColumnToggle,
    handleBack,
    handleReset,
    isStepComplete,
    buildJoinTransformation,
    resetForm
  }
} 