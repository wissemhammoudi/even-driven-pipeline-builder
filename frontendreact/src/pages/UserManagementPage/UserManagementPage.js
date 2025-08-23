import React from 'react';
import { useUserManagement } from './useUserManagement';
import { UserManagementDisplay } from './UserManagementDisplay';

const UserManagementPage = () => {
  const userManagementLogic = useUserManagement();
  
  return <UserManagementDisplay {...userManagementLogic} />;
};

export default UserManagementPage;
