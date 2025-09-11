import React from 'react'
import SearchFilter from '../../common/filters/SearchFilter'
import DateFilter from '../../common/filters/DateFilter'
import TypeFilter from '../../common/filters/TypeFilter'
import ActiveFiltersIndicator from '../../common/filters/ActiveFiltersIndicator'

const PipelineFilters = ({
  searchTerm,
  setSearchTerm,
  dateFilter,
  setDateFilter,
  showDeprecated,
  setShowDeprecated,
  onClearFilters
}) => (
  <>
    <div className='bg-white shadow rounded-lg p-4'>
      <div className='flex flex-wrap gap-6 items-end'>
        <div className='flex-1 min-w-64'>
          <SearchFilter searchTerm={searchTerm} setSearchTerm={setSearchTerm} />
        </div>
        <DateFilter dateFilter={dateFilter} setDateFilter={setDateFilter} />
        <TypeFilter isActive={showDeprecated} onToggle={setShowDeprecated} />
      </div>
    </div>
    <ActiveFiltersIndicator
      filters={[
        searchTerm
          ? {
              label: 'Search',
              value: String(searchTerm),
              colorClass: 'bg-blue-100 text-blue-800'
            }
          : null,
        dateFilter
          ? {
              label: 'Date',
              value:
                typeof dateFilter === 'object'
                  ? JSON.stringify(dateFilter)
                  : String(dateFilter),
              colorClass: 'bg-green-100 text-green-800'
            }
          : null,
        showDeprecated
          ? {
              label: 'Type',
              value: 'Deprecated',
              colorClass: 'bg-yellow-100 text-yellow-800'
            }
          : null
      ].filter(Boolean)}
    />
  </>
)

export default PipelineFilters
