
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || ''

export const API_CONFIG = {
  baseURL: API_BASE_URL,
  timeout: 300000,
  headers: {
    'Content-Type': 'application/json'
  }
}

export const STORAGE_KEYS = {
  USER: 'user',
  TOKEN: 'token',
  LOGIN_STATUS: 'login_status',
  CURRENT_PAGE: 'current_page',
  PIPELINE_STEPS: 'pipeline_steps',
  COLUMN_FUNCTIONS: 'column_functions',
  JOIN_TRANSFORMATIONS: 'join_transformations',
  AGENTIC_TRANSFORMATIONS: 'agentic_transformations'
}

export const DEFAULTS = {
  PAGE_SIZE: 10,
  MAX_FILE_SIZE: 10 * 1024 * 1024,
  TIMEOUT: 300000,
  RETRY_ATTEMPTS: 3
}

export const VALIDATION = {
  PIPELINE_NAME: {
    MIN_LENGTH: 3,
    MAX_LENGTH: 50,
    PATTERN: /^[a-zA-Z0-9\s\-_]+$/
  },
  EMAIL: {
    PATTERN: /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  },
  PASSWORD: {
    MIN_LENGTH: 8,
    PATTERN: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/
  }
}
