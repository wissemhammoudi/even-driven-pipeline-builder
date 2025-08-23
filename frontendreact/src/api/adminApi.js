import { api } from '../utils/api';

export const adminAPI = {
  // Get all users with filtering and pagination
  getAllUsers: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.search) queryParams.append('search', params.search);
    if (params.role && params.role !== 'all') queryParams.append('role', params.role);
    if (params.limit) queryParams.append('limit', params.limit);
    if (params.offset) queryParams.append('offset', params.offset);
    
    const queryString = queryParams.toString();
    return api.get(`/api/v1/users/admin/all${queryString ? `?${queryString}` : ''}`);
  },
  
  // Get user by ID
  getUserById: (userId) => api.get(`/api/v1/users/admin/${userId}`),
  
  // Create new user
  createUser: (userData) => api.post('/api/v1/users/admin/create', userData),
  
  // Update user
  updateUser: (userId, userData) => api.patch(`/api/v1/users/admin/${userId}`, userData),
  
  // Delete user
  deleteUser: (userId) => api.delete(`/api/v1/users/admin/${userId}`),
  
  // Bulk delete users
  bulkDeleteUsers: (userIds) => api.post('/api/v1/users/admin/bulk-delete', { user_ids: userIds }),
};
