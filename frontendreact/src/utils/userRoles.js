export const UserRole = {
  USER: 'user',
  ADMIN: 'admin'
};

export const UserRoleValues = Object.values(UserRole);

export const isAdminRole = (role) => role === UserRole.ADMIN;
export const isUserRole = (role) => role === UserRole.USER;
