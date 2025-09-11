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
    <div className='bg-white shadow rounded-lg p-4'>
      <div className='flex flex-wrap gap-6 items-end'>
        <div className='flex-1 min-w-64'>
          <SearchFilter searchTerm={searchTerm} setSearchTerm={setSearchTerm} />
        </div>
        <div className='flex flex-col space-y-1'>
          <label htmlFor="role-filter" className="block text-sm font-medium text-gray-700">
            Role Filter
          </label>
          <select
            id="role-filter"
            value={roleFilter || ''}
            onChange={(e) => setRoleFilter(e.target.value || null)}
            className='w-48 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500'
          >
            <option value="">All Roles</option>
            <option value="admin">Admin</option>
            <option value="user">User</option>
          </select>
        </div>
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
