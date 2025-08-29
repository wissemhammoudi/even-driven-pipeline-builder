import { api } from '../utils/api';

export const adminAPI = {
  getAllUsers: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.search) queryParams.append('search', params.search);
    if (params.role && params.role !== 'all') queryParams.append('role', params.role);
    if (params.limit) queryParams.append('limit', params.limit);
    if (params.offset) queryParams.append('offset', params.offset);
    
    const queryString = queryParams.toString();
    const url = `/api/v1/users/admin/all${queryString ? `?${queryString}` : ''}`;
    
    console.log('🌐 Making API call to:', url);
    console.log('🌐 With params:', params);
    
    return api.get(url);
  },
  
  getUserById: (userId) => api.get(`/api/v1/users/admin/${userId}`),
  createUser: (userData) => api.post('/api/v1/users/admin/create', userData),
  updateUser: (userId, userData) => api.patch(`/api/v1/users/admin/${userId}`, userData),
  deleteUser: (userId) => api.delete(`/api/v1/users/admin/${userId}`),
  bulkDeleteUsers: (userIds) => api.post('/api/v1/users/admin/bulk-delete', { user_ids: userIds }),
};
