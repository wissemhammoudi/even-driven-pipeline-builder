import { UserRole } from './userRoles';

export const decodeJWTToken = token => {
  try {
    const base64Url = token.split('.')[1]
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map(function (c) {
          return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)
        })
        .join('')
    )

    const payload = JSON.parse(jsonPayload)

    let userRole = UserRole.USER
    
    if (payload.role) {
      userRole = payload.role
    } else if (payload.realm_access?.roles && payload.realm_access.roles.length > 0) {
      userRole = payload.realm_access.roles[0]
    } else if (payload.resource_access && payload.aud) {
      const clientRoles = payload.resource_access[payload.aud]?.roles
      if (clientRoles && clientRoles.length > 0) {
        userRole = clientRoles[0]
      }
    } else if (payload.groups && payload.groups.length > 0) {
      const adminGroup = payload.groups.find(group => group.includes('admin'))
      if (adminGroup) {
        userRole = UserRole.ADMIN
      }
    }

    const user = {
      user_id: payload.sub || payload.user_id, 
      username: payload.preferred_username || payload.username, 
      email: payload.email,
      first_name: payload.given_name || payload.first_name, 
      last_name: payload.family_name || payload.last_name, 
      role: userRole
    }

    return user
  } catch (error) {
    return null
  }
}