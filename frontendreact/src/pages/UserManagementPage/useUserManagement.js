import { useState, useEffect } from 'react';
import useAuthStore from '../../store/authStore';
import { adminAPI } from '../../api/adminApi';
import toast from 'react-hot-toast';
import { UserRole } from '../../utils/userRoles';

export const useUserManagement = () => {
  const authStore = useAuthStore();
  const { user, isAdmin } = authStore;
  
  const checkIsAdmin = () => {
    const currentUser = authStore.getCurrentUser();
    const adminStatus = authStore.isAdmin();
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

  useEffect(() => {
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
      console.error('Failed to create user:', error);
      toast.error(error.response?.data?.detail || 'Failed to create user');
    }
  };

  const handleUpdateUser = async () => {
    try {
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
