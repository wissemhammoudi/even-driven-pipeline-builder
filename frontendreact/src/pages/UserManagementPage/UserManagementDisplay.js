import React from 'react';
import Card from '../../components/common/Card/Card';
import Button from '../../components/common/Button/Button';
import { UserRole } from '../../utils/userRoles';
import { 
  PlusIcon as Plus
} from '@heroicons/react/24/outline';
import PageHeader from '../../components/common/PageHeader';
import UserFilters from '../../components/features/UserManagement/UserFilters';
import UserTable from '../../components/features/UserManagement/UserTable';
import UserModal from '../../components/features/UserManagement/UserModal';
import Pagination from '../../components/common/Pagination/Pagination';

export const UserManagementDisplay = ({
  user,
  isAdmin,
  users,
  loading,
  searchTerm,
  roleFilter,
  selectedUsers,
  showCreateDialog,
  showEditDialog,
  editingUser,
  currentPage,
  totalUsers,
  hasMore,
  pageSize,
  formData,
  
  checkIsAdmin,
  setShowCreateDialog,
  setShowEditDialog,
  setEditingUser,
  setFormData,
  handleCreateUser,
  handleUpdateUser,
  handleDeleteUser,
  handleBulkDelete,
  handleEditUser,
  resetForm,
  handleSearch,
  handleRoleFilterChange,
  handlePageChange,
  handleUserSelection,
  handleSelectAll
}) => {
  
  if (!isAdmin && !checkIsAdmin()) {
    return (
      <div className="container mx-auto p-6">
        <Card>
          <div className="text-center">
            <h2 className="text-xl font-semibold text-gray-900 mb-2">Access Denied</h2>
            <p className="text-gray-600">
              You need admin privileges to access this page.
            </p>
            <div className="mt-4 text-sm text-gray-500">
              <p>Debug Info:</p>
              <p>Username: {user?.username}</p>
              <p>Role: {user?.role}</p>
              <p>Mapped Role: {user?.mapped_role}</p>
              <p>isAdmin: {isAdmin ? 'true' : 'false'}</p>
            </div>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className='space-y-6'>
      <PageHeader
        title='User Management'
        subtitle='Manage users, roles, and permissions'
        actions={
          <Button 
            onClick={() => setShowCreateDialog(true)}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          >
            <Plus className="w-4 h-4 mr-2" />
            Create User
          </Button>
        }
      />
      
      <UserFilters
        searchTerm={searchTerm}
        setSearchTerm={handleSearch}
        roleFilter={roleFilter}
        setRoleFilter={handleRoleFilterChange}
        onClearFilters={() => {
          handleSearch('');
          handleRoleFilterChange(null);
        }}
      />
      
      <div className='bg-white shadow rounded-lg'>
        <div className='px-4 py-5 sm:p-6'>
          {loading ? (
            <div className='flex flex-col items-center justify-center py-12'>
              <div className='animate-spin rounded-full h-8 w-8 border-b-2 border-primary mb-4'></div>
              <p className='text-gray-500'>Loading users...</p>
            </div>
          ) : users.length === 0 ? (
            <div className='text-center py-8'>
              <p className='text-gray-500'>No users found.</p>
            </div>
          ) : (
            <div className='space-y-8'>
              <UserTable
                users={users}
                title={`Users (${totalUsers} total)`}
                onEdit={handleEditUser}
                onDelete={handleDeleteUser}
                selectedUsers={selectedUsers}
                onUserSelection={handleUserSelection}
                onSelectAll={handleSelectAll}
                isAdmin={isAdmin}
              />
              
              {totalUsers > pageSize && (
                <Pagination
                  currentPage={currentPage}
                  totalPages={Math.ceil(totalUsers / pageSize)}
                  pageSize={pageSize}
                  totalItems={totalUsers}
                  onPageChange={handlePageChange}
                />
              )}
            </div>
          )}
        </div>
      </div>

      {selectedUsers.length > 0 && (
        <div className='bg-white shadow rounded-lg p-4'>
          <div className='flex items-center justify-between'>
            <span className='text-sm text-gray-700'>
              {selectedUsers.length} user(s) selected
            </span>
            <Button
              variant="secondary"
              onClick={() => handleBulkDelete(selectedUsers)}
              className="bg-red-600 hover:bg-red-700 text-white"
            >
              Delete Selected
            </Button>
          </div>
        </div>
      )}

      {/* Create User Modal */}
      <UserModal
        isOpen={showCreateDialog}
        onClose={() => setShowCreateDialog(false)}
        title="Create New User"
        formData={formData}
        setFormData={setFormData}
        onSubmit={handleCreateUser}
        isEdit={false}
      />

      {/* Edit User Modal */}
      <UserModal
        isOpen={showEditDialog}
        onClose={() => {
          setShowEditDialog(false);
          setEditingUser(null);
        }}
        title="Edit User"
        formData={formData}
        setFormData={setFormData}
        onSubmit={handleUpdateUser}
        isEdit={true}
      />
    </div>
  );
};
