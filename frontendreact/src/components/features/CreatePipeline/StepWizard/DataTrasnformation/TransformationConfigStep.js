import React, { useState, useMemo, useCallback, useRef } from 'react'
import { TabButton, findIngestionStep, hasIngestionStep } from '../shared/utils'
import { useDatabaseConnection } from '../shared/useDatabaseConnection'
import { useSchemaInfo } from '../shared/useSchemaInfo'
import { useFunctionMapping } from './useFunctionMapping'
import { useTransformationState } from './useTransformationState'
import ColumnTransformationTab from './ColumnTransformationTab'
import AgenticTransformationTab from './AgenticTransformationTab'
import JoinTransformationTab from './JoinTransformationTab'
import { extractErrorMessage } from '../../../../../utils/errorHandler'
import { StepTypeEnum } from '../utils'

const TransformationConfigStep = ({
  formData,
  utilityType,
  allPipelineSteps,
  plugins,
  pluginConfigSchemas,
  onInputChange
}) => {
  const [activeTab, setActiveTab] = useState('column')

  const ingestionStep = useMemo(() => findIngestionStep(allPipelineSteps), [allPipelineSteps])
  const hasIngestionStepData = useMemo(() => hasIngestionStep(ingestionStep), [ingestionStep])

  const combinedPipelineSteps = useMemo(() => {
    const currentStep = {
      type: StepTypeEnum.DATA_TRANSFORMATION,
      step_config: formData.step_config
    }
    return [...allPipelineSteps, currentStep]
  }, [allPipelineSteps, formData.step_config])

  const {
    connectionConfig,
    isLoadingConnection,
    connectionError,
    sourceConfigDisplay
  } = useDatabaseConnection(combinedPipelineSteps, 'transformation')

  const {
    schemaInfo,
    isLoadingSchema,
    schemaError,
    getAllTables
  } = useSchemaInfo(connectionConfig)

  const {
    functionMapping,
    transformationSchema,
    isLoadingFunctions,
    functionLoadError
  } = useFunctionMapping(formData.step_config.tool || utilityType)

  const availableTables = useMemo(() => getAllTables(), [getAllTables])

  const getSelectedTablesFromIngestion = useCallback(() => {
    if (!ingestionStep?.step_config?.table_sync_config) {
      return availableTables
    }

    const tableSyncConfig = ingestionStep.step_config.table_sync_config
    let selectedTableNames = []

    if (Array.isArray(tableSyncConfig)) {
      selectedTableNames = tableSyncConfig
    } else if (typeof tableSyncConfig === 'object') {
      if (tableSyncConfig.tables) {
        selectedTableNames = tableSyncConfig.tables.map(t => t.table_name)
      } else {
        selectedTableNames = Object.keys(tableSyncConfig)
      }
    }

    return availableTables.filter(table => selectedTableNames.includes(table.name))
  }, [ingestionStep?.step_config?.table_sync_config, availableTables])

  const tablesForTransformation = useMemo(() => getSelectedTablesFromIngestion(), [getSelectedTablesFromIngestion])

  const getFlattenedTableConfig = useCallback(() => {
    const flattenedConfig = {}
    
    tablesForTransformation.forEach(table => {
      for (const [schemaName, schemaTables] of Object.entries(schemaInfo)) {
        if (schemaTables[table.name]) {
          flattenedConfig[table.name] = schemaTables[table.name]
          break
        }
      }
    })
    
    return flattenedConfig
  }, [tablesForTransformation, schemaInfo])

  const tableConfig = useMemo(() => getFlattenedTableConfig(), [getFlattenedTableConfig])

  const stableOnInputChange = useCallback((field, value) => {
    onInputChange(field, value)
  }, [onInputChange])
  
  const {
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
  } = useTransformationState(formData, stableOnInputChange, tableConfig)

  const columnTabProps = useMemo(() => ({
    availableTables: tablesForTransformation || [],
    tableConfig: tableConfig || {},
    functionMapping: functionMapping || {},
    transformationSchema: transformationSchema || {},
    columnFunctions: columnFunctions || {},
    onColumnFunctionChange: handleColumnFunctionChange,
    updateTableSyncConfig: updateTableSyncConfig,
    hasIngestionStep: hasIngestionStepData,
    ingestionStep: ingestionStep
  }), [
    tablesForTransformation,
    tableConfig,
    functionMapping,
    transformationSchema,
    columnFunctions,
    handleColumnFunctionChange,
    updateTableSyncConfig,
    hasIngestionStepData,
    ingestionStep
  ])

  const joinTabProps = useMemo(() => ({
    availableTables: tablesForTransformation,
    tableConfig: tableConfig,
    joinTransformations: joinTransformations,
    onAddJoinTransformation: handleAddJoinTransformation,
    onRemoveJoinTransformation: handleRemoveJoinTransformation,
    onClearAllJoins: handleClearAllJoins
  }), [
    tablesForTransformation,
    tableConfig,
    joinTransformations,
    handleAddJoinTransformation,
    handleRemoveJoinTransformation,
    handleClearAllJoins
  ])

  const agenticTabProps = useMemo(() => ({
    sourceConfigDisplay: sourceConfigDisplay,
    agenticTransformations: agenticTransformations,
    onAddAgenticTransformation: handleAddAgenticTransformation,
    onRemoveAgenticTransformation: handleRemoveAgenticTransformation
  }), [
    sourceConfigDisplay,
    agenticTransformations,
    handleAddAgenticTransformation,
    handleRemoveAgenticTransformation
  ])

  const columnTab = useMemo(() => (
    <ColumnTransformationTab {...columnTabProps} />
  ), [columnTabProps])

  const joinTab = useMemo(() => (
    <JoinTransformationTab {...joinTabProps} />
  ), [joinTabProps])

  const agenticTab = useMemo(() => (
    <AgenticTransformationTab {...agenticTabProps} />
  ), [agenticTabProps])

  if (isLoadingConnection || isLoadingSchema) {
    return (
      <div className='space-y-6'>
        <div className='bg-blue-50 border border-blue-200 rounded-lg p-4'>
          <h4 className='text-sm font-medium text-blue-900 mb-2'>Loading...</h4>
          <p className='text-sm text-blue-700'>Loading table configuration...</p>
        </div>
      </div>
    )
  }

  if (connectionError || schemaError) {
    const errorMessage = extractErrorMessage(connectionError || schemaError, 'An error occurred')
    
    return (
      <div className='space-y-6'>
        <div className='bg-red-50 border border-red-200 rounded-lg p-4'>
          <h4 className='text-sm font-medium text-red-900 mb-2'>Configuration Error</h4>
          <p className='text-sm text-red-700'>{errorMessage}</p>
        </div>
      </div>
    )
  }

  return (
    <div className='space-y-6'>
      <div className='bg-blue-50 border border-blue-200 rounded-lg p-4'>
        <h4 className='text-sm font-medium text-blue-900 mb-2'>
          Data Transformation Configuration
        </h4>
        <p className='text-sm text-blue-700'>
          Configure how your data should be transformed using different methods
        </p>
        {hasIngestionStepData && (
          <div className='mt-2 text-xs text-blue-600'>
            <p><strong>Using tables from ingestion step:</strong> {tablesForTransformation.length} of {availableTables.length} tables</p>
            <p><strong>Selected tables:</strong> {tablesForTransformation.map(t => t.name).join(', ')}</p>
            <p><strong>Table config keys:</strong> {Object.keys(tableConfig).join(', ')}</p>
          </div>
        )}
      </div>

      <div className='flex space-x-2 border-b border-gray-200'>
        <TabButton
          active={activeTab === 'column'}
          onClick={() => setActiveTab('column')}
        >
          Column Transformations
        </TabButton>
        <TabButton
          active={activeTab === 'join'}
          onClick={() => setActiveTab('join')}
        >
          Table Joins
        </TabButton>
        <TabButton
          active={activeTab === 'agentic'}
          onClick={() => setActiveTab('agentic')}
        >
          AI-Powered
        </TabButton>
      </div>

      {activeTab === 'column' && columnTab}
      {activeTab === 'join' && joinTab}
      {activeTab === 'agentic' && agenticTab}
    </div>
  )
}

export default React.memo(TransformationConfigStep)
