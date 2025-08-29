import React from 'react'
import SearchFilter from '../../common/filters/SearchFilter'
import TypeFilter from '../../common/filters/TypeFilter'
import ActiveFiltersIndicator from '../../common/filters/ActiveFiltersIndicator'

const UserFilters = ({
  searchTerm,
  setSearchTerm,
  roleFilter,
  setRoleFilter,
  onClearFilters
}) => (
  <>
    <div className='flex flex-wrap gap-4 items-end'>
      <SearchFilter searchTerm={searchTerm} setSearchTerm={setSearchTerm} />
      <div className='flex items-center space-x-2'>
        <label className='text-sm font-medium text-gray-700'>Role:</label>
        <select
          value={roleFilter || ''}
          onChange={(e) => setRoleFilter(e.target.value || null)}
          className='block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm'
        >
          <option value="">All Roles</option>
          <option value="admin">Admin</option>
          <option value="user">User</option>
        </select>
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
        roleFilter
          ? {
              label: 'Role',
              value: roleFilter.charAt(0).toUpperCase() + roleFilter.slice(1),
              colorClass: 'bg-green-100 text-green-800'
            }
          : null
      ].filter(Boolean)}
    />
  </>
)

export default UserFilters
