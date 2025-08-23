import React, { useState, useEffect } from 'react';
import useAuthStore from '../../store/authStore';
import { adminAPI } from '../../api/adminApi';
import toast from 'react-hot-toast';
import Card from '../../components/common/Card/Card';
import Button from '../../components/common/Button/Button';
import Input from '../../components/common/Input/Input';
import { 
  ArrowPathIcon as Loader2, 
  PlusIcon as Plus, 
  PencilIcon as Edit, 
  TrashIcon as Trash2, 
  MagnifyingGlassIcon as Search, 
  FunnelIcon as Filter 
} from '@heroicons/react/24/outline';

const UserManagementPage = () => {
  const authStore = useAuthStore();
  const { user, isAdmin } = authStore;
  
  // Alternative way to check admin status
  const checkIsAdmin = () => {
    const currentUser = authStore.getCurrentUser();
    const adminStatus = authStore.isAdmin();
    console.log('Alternative admin check - Current user:', currentUser);
    console.log('Alternative admin check - isAdmin result:', adminStatus);
    return adminStatus;
  };
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [roleFilter, setRoleFilter] = useState('all');
  const [selectedUsers, setSelectedUsers] = useState([]);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [showEditDialog, setShowEditDialog] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  
  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const [totalUsers, setTotalUsers] = useState(0);
  const [hasMore, setHasMore] = useState(false);
  const [pageSize] = useState(20);
  
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    password: '',
    role: 'user'
  });

  useEffect(() => {
    console.log('useEffect - isAdmin changed:', isAdmin);
    if (isAdmin || checkIsAdmin()) {
      loadUsers();
    }
  }, [isAdmin]);

  const loadUsers = async (page = 1, search = searchTerm, role = roleFilter) => {
    try {
      setLoading(true);
      const offset = (page - 1) * pageSize;
      
      const response = await adminAPI.getAllUsers({
        search: search || undefined,
        role: role || undefined,
        limit: pageSize,
        offset: offset
      });
      
      if (response && response.users) {
        setUsers(response.users);
        setTotalUsers(response.total);
        setHasMore(response.has_more);
        setCurrentPage(page);
      } else {
        setUsers([]);
        setTotalUsers(0);
        setHasMore(false);
      }
    } catch (error) {
      console.error('Failed to load users:', error);
      toast.error('Failed to load users');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateUser = async () => {
    try {
      // Form validation
      if (!formData.username || !formData.email || !formData.password) {
        toast.error('Username, email, and password are required');
        return;
      }
      
      if (formData.password.length < 8) {
        toast.error('Password must be at least 8 characters long');
        return;
      }
      
      // Debug logging
      console.log('DEBUG: Form data being sent:', formData);
      console.log('DEBUG: Password length:', formData.password.length);
      console.log('DEBUG: Role value:', formData.role);
      console.log('DEBUG: Role type:', typeof formData.role);
      
      const response = await adminAPI.createUser(formData);
      toast.success('User created successfully');
      setShowCreateDialog(false);
      resetForm();
      loadUsers();
    } catch (error) {
      console.error('Failed to create user:', error);
      console.error('Error response:', error.response);
      console.error('Error data:', error.response?.data);
      toast.error(error.response?.data?.detail || 'Failed to create user');
    }
  };

  const handleUpdateUser = async () => {
    try {
      // Form validation
      if (!formData.username || !formData.email) {
        toast.error('Username and email are required');
        return;
      }
      
      await adminAPI.updateUser(editingUser.user_id, formData);
      toast.success('User updated successfully');
      setShowEditDialog(false);
      setEditingUser(null);
      resetForm();
      loadUsers();
    } catch (error) {
      console.error('Failed to update user:', error);
      toast.error(error.response?.data?.detail || 'Failed to update user');
    }
  };

  const handleDeleteUser = async (userId) => {
    if (!window.confirm('Are you sure you want to delete this user?')) return;
    
    try {
      await adminAPI.deleteUser(userId);
      toast.success('User deleted successfully');
      loadUsers();
    } catch (error) {
      console.error('Failed to delete user:', error);
      toast.error('Failed to delete user');
    }
  };

  const handleBulkDelete = async () => {
    if (selectedUsers.length === 0) return;
    if (!window.confirm(`Are you sure you want to delete ${selectedUsers.length} users?`)) return;
    
    try {
      await adminAPI.bulkDeleteUsers(selectedUsers);
      toast.success(`${selectedUsers.length} users deleted successfully`);
      setSelectedUsers([]);
      loadUsers();
    } catch (error) {
      console.error('Failed to delete users:', error);
      toast.error('Failed to delete users');
    }
  };

  const handleEditUser = (user) => {
    setEditingUser(user);
    setFormData({
      username: user.username,
      email: user.email,
      first_name: user.first_name || '',
      last_name: user.last_name || '',
      password: '',
      role: user.role
    });
    setShowEditDialog(true);
  };

  const resetForm = () => {
    setFormData({
      username: '',
      email: '',
      first_name: '',
      last_name: '',
      password: '',
      role: 'user'
    });
  };

  // Handle search with debouncing
  const handleSearch = (value) => {
    setSearchTerm(value);
    setCurrentPage(1); // Reset to first page
    // Debounce the search to avoid too many API calls
    setTimeout(() => {
      loadUsers(1, value, roleFilter);
    }, 300);
  };

  // Handle role filter change
  const handleRoleFilterChange = (value) => {
    setRoleFilter(value);
    setCurrentPage(1); // Reset to first page
    loadUsers(1, searchTerm, value);
  };

  // Handle pagination
  const handlePageChange = (page) => {
    setCurrentPage(page);
    loadUsers(page, searchTerm, roleFilter);
  };

  const handleUserSelection = (userId, checked) => {
    if (checked) {
      setSelectedUsers([...selectedUsers, userId]);
    } else {
      setSelectedUsers(selectedUsers.filter(id => id !== userId));
    }
  };

  const handleSelectAll = (checked) => {
    if (checked) {
      setSelectedUsers(users.map(user => user.user_id));
    } else {
      setSelectedUsers([]);
    }
  };

  // Debug logging
  console.log('UserManagementPage - Current user:', user);
  console.log('UserManagementPage - isAdmin result:', isAdmin);
  console.log('UserManagementPage - User role:', user?.role);
  console.log('UserManagementPage - User mapped_role:', user?.mapped_role);
  
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
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">User Management</h1>
          <p className="text-gray-600">
            Manage users, roles, and permissions
          </p>
        </div>
        <Button onClick={() => setShowCreateDialog(true)}>
          <Plus className="w-4 h-4 mr-2" />
          Create User
        </Button>
      </div>

      {/* Filters and Search */}
      <Card>
        <div className="flex gap-4 items-center">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <Input
                placeholder="Search users..."
                value={searchTerm}
                onChange={(e) => handleSearch(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-gray-400" />
            <select 
              value={roleFilter} 
              onChange={(e) => handleRoleFilterChange(e.target.value)}
              className="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="all">All Roles</option>
              <option value="admin">Admin</option>
              <option value="user">User</option>
            </select>
          </div>
        </div>
      </Card>

      {/* Bulk Actions */}
      {selectedUsers.length > 0 && (
        <Card>
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">
              {selectedUsers.length} user(s) selected
            </span>
            <Button 
              variant="secondary"
              onClick={handleBulkDelete}
              className="bg-red-600 hover:bg-red-700 text-white"
            >
              <Trash2 className="w-4 h-4 mr-2" />
              Delete Selected
            </Button>
          </div>
        </Card>
      )}

      {/* Users Table */}
      <Card>
        <div className="mb-4">
          <h3 className="text-lg font-medium text-gray-900">Users ({totalUsers})</h3>
          <p className="text-sm text-gray-600">
            Manage user accounts and permissions
          </p>
        </div>
        
        {loading ? (
          <div className="flex justify-center items-center py-8">
            <Loader2 className="w-8 h-8 animate-spin" />
          </div>
        ) : (
          <>
            <div className="overflow-hidden">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-12">
                      <input
                        type="checkbox"
                        checked={selectedUsers.length === users.length && users.length > 0}
                        onChange={(e) => handleSelectAll(e.target.checked)}
                        className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                      />
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      User
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Email
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Role
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Created
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {users.map((user) => (
                    <tr key={user.user_id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <input
                          type="checkbox"
                          checked={selectedUsers.includes(user.user_id)}
                          onChange={(e) => handleUserSelection(user.user_id, e.target.checked)}
                          className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                        />
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div>
                          <div className="font-medium text-gray-900">
                            {user.first_name && user.last_name 
                              ? `${user.first_name} ${user.last_name}`
                              : user.username
                            }
                          </div>
                          <div className="text-sm text-gray-500">
                            @{user.username}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {user.email}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          user.role === 'admin' 
                            ? 'bg-blue-100 text-blue-800' 
                            : 'bg-gray-100 text-gray-800'
                        }`}>
                          {user.role}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          user.is_deleted 
                            ? 'bg-red-100 text-red-800' 
                            : 'bg-green-100 text-green-800'
                        }`}>
                          {user.is_deleted ? 'Deleted' : 'Active'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {new Date(user.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <div className="flex gap-2 justify-end">
                          <Button
                            variant="secondary"
                            onClick={() => handleEditUser(user)}
                            className="px-3 py-1 text-xs"
                          >
                            <Edit className="w-4 h-4" />
                          </Button>
                          <Button
                            variant="secondary"
                            onClick={() => handleDeleteUser(user.user_id)}
                            className="px-3 py-1 text-xs bg-red-600 hover:bg-red-700 text-white"
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            
            {/* Pagination Controls */}
            {totalUsers > pageSize && (
              <div className="flex items-center justify-between px-4 py-3 border-t">
                <div className="text-sm text-gray-600">
                  Showing {((currentPage - 1) * pageSize) + 1} to {Math.min(currentPage * pageSize, totalUsers)} of {totalUsers} users
                </div>
                <div className="flex gap-2">
                  <Button
                    variant="secondary"
                    onClick={() => handlePageChange(currentPage - 1)}
                    disabled={currentPage === 1}
                    className="px-3 py-1 text-sm"
                  >
                    Previous
                  </Button>
                  <span className="flex items-center px-3 text-sm text-gray-600">
                    Page {currentPage} of {Math.ceil(totalUsers / pageSize)}
                  </span>
                  <Button
                    variant="secondary"
                    onClick={() => handlePageChange(currentPage + 1)}
                    disabled={!hasMore}
                    className="px-3 py-1 text-sm"
                  >
                    Next
                  </Button>
                </div>
              </div>
            )}
          </>
        )}
      </Card>

      {/* Create User Dialog */}
      {showCreateDialog && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Create New User</h3>
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <Input
                    name="username"
                    label="Username"
                    value={formData.username}
                    onChange={(e) => setFormData({...formData, username: e.target.value})}
                    placeholder="Enter username"
                  />
                  <Input
                    name="email"
                    label="Email"
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({...formData, email: e.target.value})}
                    placeholder="Enter email"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <Input
                    name="first_name"
                    label="First Name"
                    value={formData.first_name}
                    onChange={(e) => setFormData({...formData, first_name: e.target.value})}
                    placeholder="Enter first name"
                  />
                  <Input
                    name="last_name"
                    label="Last Name"
                    value={formData.last_name}
                    onChange={(e) => setFormData({...formData, last_name: e.target.value})}
                    placeholder="Enter last name"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <Input
                    name="password"
                    label="Password"
                    type="password"
                    value={formData.password}
                    onChange={(e) => setFormData({...formData, password: e.target.value})}
                    placeholder="Enter password"
                  />
                  <div>
                    <label className="block text-sm font-medium mb-1">Role</label>
                    <select 
                      value={formData.role} 
                      onChange={(e) => setFormData({...formData, role: e.target.value})}
                      className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
                    >
                      <option value="user">User</option>
                      <option value="admin">Admin</option>
                    </select>
                  </div>
                </div>
              </div>
              <div className="flex gap-2 mt-6">
                <Button variant="secondary" onClick={() => setShowCreateDialog(false)}>
                  Cancel
                </Button>
                <Button onClick={handleCreateUser}>
                  Create User
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Edit User Dialog */}
      {showEditDialog && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Edit User</h3>
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <Input
                    name="edit-username"
                    label="Username"
                    value={formData.username}
                    onChange={(e) => setFormData({...formData, username: e.target.value})}
                    placeholder="Enter username"
                  />
                  <Input
                    name="edit-email"
                    label="Email"
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({...formData, email: e.target.value})}
                    placeholder="Enter email"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <Input
                    name="edit-first_name"
                    label="First Name"
                    value={formData.first_name}
                    onChange={(e) => setFormData({...formData, first_name: e.target.value})}
                    placeholder="Enter first name"
                  />
                  <Input
                    name="edit-last_name"
                    label="Last Name"
                    value={formData.last_name}
                    onChange={(e) => setFormData({...formData, last_name: e.target.value})}
                    placeholder="Enter last name"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Role</label>
                  <select 
                    value={formData.role} 
                    onChange={(e) => setFormData({...formData, role: e.target.value})}
                    className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
                  >
                    <option value="user">User</option>
                    <option value="admin">Admin</option>
                  </select>
                </div>
              </div>
              <div className="flex gap-2 mt-6">
                <Button variant="secondary" onClick={() => setShowEditDialog(false)}>
                  Cancel
                </Button>
                <Button onClick={handleUpdateUser}>
                  Update User
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default UserManagementPage;
