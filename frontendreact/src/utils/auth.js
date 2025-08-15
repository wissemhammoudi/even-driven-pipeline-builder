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

    const user = {
      user_id: payload.user_id,
      username: payload.username,
      email: payload.email,
      first_name: payload.first_name,
      last_name: payload._last_name,
      role: payload.role
    }

    return user
  } catch (error) {
    return null
  }
}