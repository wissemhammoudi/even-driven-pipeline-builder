import React from 'react'
import { ConfigHeader, WarningState } from '../shared/utils'
import { useJoinTransformation } from './JoinTransformationTab/useJoinTransformation'
import JoinStepIndicator from './JoinTransformationTab/JoinStepIndicator'
import Step1BasicInfo from './JoinTransformationTab/Step1BasicInfo'
import Step2TableSelection from './JoinTransformationTab/Step2TableSelection'
import Step3TableConfiguration from './JoinTransformationTab/Step3TableConfiguration'
import JoinSummary from './JoinTransformationTab/JoinSummary'

const JoinTransformationTab = ({
  availableTables,
  tableConfig = {},
  joinTransformations,
  onAddJoinTransformation,
  onRemoveJoinTransformation,
  onClearAllJoins
}) => {
  const {
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
  } = useJoinTransformation(tableConfig)

  const handleAddJoin = () => {
    const newJoin = buildJoinTransformation()
    if (newJoin) {
      onAddJoinTransformation(newJoin)
      resetForm()
    }
  }

  if (availableTables.length === 0) {
    return (
      <WarningState 
        title="No Tables Available"
        message="No tables available for join transformations. Configure the source database first."
      />
    )
  }

  const renderStep = () => {
    switch (step) {
      case 1:
        return (
          <Step1BasicInfo
            modelName={modelName}
            setModelName={setModelName}
            primaryTable={primaryTable}
            setPrimaryTable={setPrimaryTable}
            availableTables={availableTables}
            onNext={handlePrimaryTableSelect}
          />
        )
      case 2:
        return (
          <Step2TableSelection
            primaryTable={primaryTable}
            modelName={modelName}
            availableTables={availableTables}
            selectedTargetTables={selectedTargetTables}
            onTableToggle={handleTargetTableToggle}
            onBack={handleBack}
            onNext={handleTargetTablesConfirm}
          />
        )
      case 3:
        return (
          <Step3TableConfiguration
            primaryTable={primaryTable}
            selectedTargetTables={selectedTargetTables}
            tableConfigs={tableConfigs}
            getTableColumns={getTableColumns}
            onConfigChange={handleTableConfigChange}
            onColumnToggle={handleColumnToggle}
            onBack={handleBack}
            onReset={handleReset}
            onComplete={handleAddJoin}
            isStepComplete={isStepComplete}
          />
        )
      default:
        return null
    }
  }

  return (
    <div className='space-y-4'>
      <ConfigHeader 
        color="blue"
        title="Table Joins"
        message="Create joins between your tables with individual configurations for each target table."
      >
        <div className='mt-2 text-xs text-blue-600'>
          <p><strong>Available Tables:</strong> {availableTables.length} tables found</p>
          {availableTables.length > 0 && (
            <p><strong>Tables:</strong> {availableTables.map(t => t.name).join(', ')}</p>
          )}
        </div>
      </ConfigHeader>

      <div className='bg-white border border-gray-200 rounded-lg p-4'>
        <JoinStepIndicator step={step} />
        {renderStep()}
      </div>

      <JoinSummary
        joinTransformations={joinTransformations}
        onRemoveJoin={onRemoveJoinTransformation}
        onClearAll={onClearAllJoins}
      />
    </div>
  )
}

export default JoinTransformationTab 