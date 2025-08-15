export function validateRequired(value, fieldName) {
  if (!value || (typeof value === 'string' && value.trim() === '')) {
    return `${fieldName} is required`;
  }
  return '';
}

export function validateEmail(email) {
  if (!email || (typeof email === 'string' && email.trim() === '')) {
    return 'Email is required';
  }
  if (typeof email !== 'string' || !/\S+@\S+\.\S+/.test(email)) {
    return 'Email is invalid';
  }
  return '';
}

export function validatePassword(password, minLength = 6) {
  if (!password) {
    return 'Password is required';
  }
  if (password.length < minLength) {
    return `Password must be at least ${minLength} characters`;
  }
  return '';
}

export function validatePasswordMatch(password, confirmPassword) {
  if (password !== confirmPassword) {
    return 'Passwords do not match';
  }
  return '';
} 
