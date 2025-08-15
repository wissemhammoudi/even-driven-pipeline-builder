import React from 'react'
import ConfigModal from './ConfigModal'
import ConfigurationsSection from './ConfigurationsSection'
import SelectionCard from './SelectionCard'
import TransformationsSection from './TransformationsSection'
import { ServerIcon, CogIcon, ArrowLeftIcon } from '@heroicons/react/24/outline'
import PageHeader from '../../common/PageHeader'
import { useNavigate } from 'react-router-dom'

const ConfigManagementView = ({
  state,
  toolStepTypes,
  transformations,
  pageSize,
  activeConfigs,
  deprecatedConfigs,
  handleToolSelect,
  handleTypeSelect,
  handleToggleTransformations,
  handleToggleDeprecated,
  handlePageChange,
  handleViewConfig,
  handleDeprecateConfig,
  closeConfigModal
}) => {
  const navigate = useNavigate();

  return (
    <div className='space-y-6'>
      <PageHeader
        title='Supported Connectors'
        subtitle='Manage step configurations for different tools and step types'
        onBackClick={() => navigate('/dashboard')}
        backIcon={ArrowLeftIcon}
      />

      <SelectionCard
        title='Tools'
        items={state.allTools}
        selectedItem={state.selectedTool}
        loading={state.loading}
        onSelect={handleToolSelect}
        icon={ServerIcon}
        emptyMessage='No tools available'
      />

      {state.selectedTool && (
        <SelectionCard
          title={`Step Types for ${state.selectedTool}`}
          items={toolStepTypes}
          selectedItem={state.selectedType}
          onSelect={handleTypeSelect}
          icon={CogIcon}
          emptyMessage='No step types found for this tool'
        />
      )}

      <TransformationsSection
        selectedTool={state.selectedTool}
        selectedType={state.selectedType}
        transformations={transformations}
        showTransformations={state.showTransformations}
        onToggleTransformations={handleToggleTransformations}
      />

      <ConfigurationsSection
        selectedTool={state.selectedTool}
        selectedType={state.selectedType}
        loading={state.loading}
        showDeprecated={state.showDeprecated}
        onToggleDeprecated={handleToggleDeprecated}
        activeConfigs={activeConfigs}
        deprecatedConfigs={deprecatedConfigs}
        currentPage={state.currentPage}
        pageSize={pageSize}
        onPageChange={handlePageChange}
        onViewConfig={handleViewConfig}
        onDeprecateConfig={handleDeprecateConfig}
      />

      <ConfigModal
        isOpen={state.showConfigModal}
        selectedConfig={state.selectedConfig}
        onClose={closeConfigModal}
      />
    </div>
  )
}

export default ConfigManagementView 