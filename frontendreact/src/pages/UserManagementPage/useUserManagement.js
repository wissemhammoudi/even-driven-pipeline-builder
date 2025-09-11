import { useState, useEffect, useCallback } from 'react';
import useAuthStore from '../../store/authStore';
import { adminAPI } from '../../api/adminApi';
import toast from 'react-hot-toast';
import { UserRole } from '../../utils/userRoles';

export const useUserManagement = () => {
  const authStore = useAuthStore();
  const { user, isAdmin } = authStore;
  
  
  
  const checkIsAdmin = useCallback(() => {
    const currentUser = authStore.getCurrentUser();
    const adminStatus = authStore.isAdmin();
    return adminStatus;
  }, [authStore]);

  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [roleFilter, setRoleFilter] = useState('all');
  const [selectedUsers, setSelectedUsers] = useState([]);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [showEditDialog, setShowEditDialog] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  
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
    role: UserRole.USER
  });

  const loadUsers = useCallback(async (page = 1, search = searchTerm, role = roleFilter) => {
    try {
      setLoading(true);
      const offset = (page - 1) * pageSize;
      
      const response = await adminAPI.getAllUsers({
        search: search || undefined,
        role: role === 'all' ? undefined : role,
        limit: pageSize,
        offset: offset
      });
      
      if (response && response.data && response.data.users) {
        setUsers(response.data.users);
        setTotalUsers(response.data.total_count || response.data.total);
        // Calculate has_more based on total_pages or use the old has_more field
        const totalPages = response.data.total_pages;
        const hasMorePages = totalPages ? page < totalPages : response.data.has_more;
        setHasMore(hasMorePages);
        setCurrentPage(page);
      } else {
        setUsers([]);
        setTotalUsers(0);
        setHasMore(false);
      }
    } catch (error) {
      toast.error('Failed to load users');
    } finally {
      setLoading(false);
    }
  }, [pageSize, searchTerm, roleFilter]);

  useEffect(() => {
    if (isAdmin || checkIsAdmin()) {
      loadUsers();
    }
  }, [isAdmin, checkIsAdmin, loadUsers]);

  const handleCreateUser = async () => {
    try {
      if (!formData.username || !formData.email || !formData.password) {
        toast.error('Username, email, and password are required');
        return;
      }
      
      if (formData.password.length < 8) {
        toast.error('Password must be at least 8 characters long');
        return;
      }
      
      const response = await adminAPI.createUser(formData);
      toast.success('User created successfully');
      setShowCreateDialog(false);
      resetForm();
      loadUsers();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create user');
    }
  };

  const handleUpdateUser = async () => {
    try {
      if (!formData.username || !formData.email) {
        toast.error('Username and email are required');
        return;
      }
      
      const updateData = {
        username: formData.username.trim(),
        email: formData.email.trim(),
        first_name: formData.first_name?.trim() || null,
        last_name: formData.last_name?.trim() || null,
        role: formData.role
      };
      
      Object.keys(updateData).forEach(key => {
        if (updateData[key] === null || updateData[key] === undefined || updateData[key] === '') {
          delete updateData[key];
        }
      });
      
      await adminAPI.updateUser(editingUser.user_id, updateData);
      toast.success('User updated successfully');
      setShowEditDialog(false);
      setEditingUser(null);
      resetForm();
      loadUsers();
    } catch (error) {
      
      toast.error(error.response?.data?.detail || 'Failed to update user');
    }
  };

  const handleDeleteUser = async (userId) => {
    try {
      const response = await adminAPI.deleteUser(userId);
      toast.success('User deleted successfully');
      loadUsers();
    } catch (error) {
      
      let errorMessage = 'Failed to delete user';
      if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.response?.status === 401) {
        errorMessage = 'Unauthorized - please log in again';
      } else if (error.response?.status === 403) {
        errorMessage = 'Forbidden - insufficient permissions';
      } else if (error.response?.status === 404) {
        errorMessage = 'User not found';
      } else if (error.response?.status >= 500) {
        errorMessage = 'Server error - please try again later';
      }
      
      toast.error(errorMessage);
    }
  };

  const handleBulkDelete = async () => {
    if (selectedUsers.length === 0) return;
    try {
      const response = await adminAPI.bulkDeleteUsers(selectedUsers);
      toast.success(`${selectedUsers.length} users deleted successfully`);
      setSelectedUsers([]);
      loadUsers();
    } catch (error) {      
      let errorMessage = 'Failed to delete users';
      if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.response?.status === 401) {
        errorMessage = 'Unauthorized - please log in again';
      } else if (error.response?.status === 403) {
        errorMessage = 'Forbidden - insufficient permissions';
      } else if (error.response?.status === 404) {
        errorMessage = 'One or more users not found';
      } else if (error.response?.status >= 500) {
        errorMessage = 'Server error - please try again later';
      }
      
      toast.error(errorMessage);
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
      role: UserRole.USER
    });
  };

  const handleSearch = (value) => {
    setSearchTerm(value);
    setCurrentPage(1); 
    setTimeout(() => {
      loadUsers(1, value, roleFilter);
    }, 300);
  };

  const handleRoleFilterChange = (value) => {
    setRoleFilter(value);
    setCurrentPage(1); 
    loadUsers(1, searchTerm, value);
  };

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

  return {
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
  };
};
