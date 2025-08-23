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
    
    // Debug logging to see what's in the JWT payload
    console.log('JWT Payload:', payload)
    console.log('Realm access:', payload.realm_access)
    console.log('Resource access:', payload.resource_access)
    console.log('Groups:', payload.groups)

    // Better role extraction from Keycloak
    let userRole = 'user' // default fallback
    
    // Check multiple possible role sources in order of preference
    if (payload.role) {
      userRole = payload.role
      console.log('Using payload.role:', userRole)
    } else if (payload.realm_access?.roles && payload.realm_access.roles.length > 0) {
      // Keycloak realm roles
      userRole = payload.realm_access.roles[0]
      console.log('Using realm_access.roles[0]:', userRole)
    } else if (payload.resource_access && payload.aud) {
      // Check client-specific roles
      const clientRoles = payload.resource_access[payload.aud]?.roles
      if (clientRoles && clientRoles.length > 0) {
        userRole = clientRoles[0]
        console.log('Using resource_access client roles:', userRole)
      }
    } else if (payload.groups && payload.groups.length > 0) {
      // Check user groups (alternative role source)
      const adminGroup = payload.groups.find(group => group.includes('admin'))
      if (adminGroup) {
        userRole = 'admin'
        console.log('Using groups admin detection:', userRole)
      }
    }
    
    console.log('Final extracted role:', userRole)

    const user = {
      user_id: payload.sub || payload.user_id, // Keycloak uses 'sub' for user ID
      username: payload.preferred_username || payload.username, // Keycloak uses 'preferred_username'
      email: payload.email,
      first_name: payload.given_name || payload.first_name, // Keycloak uses 'given_name'
      last_name: payload.family_name || payload.last_name, // Keycloak uses 'family_name'
      role: userRole
    }

    return user
  } catch (error) {
    console.error('Error decoding JWT token:', error)
    return null
  }
}