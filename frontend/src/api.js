const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:5000/api';

export async function apiFetch(path, options = {}) {
  const url = `${BASE_URL}${path}`;

  const token = localStorage.getItem('token');

  // Merge headers
  const headers = {
    ...(options.headers || {})
  };

  // for content type not set
  if (options.body && !headers['Content-Type'] && !(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json';
  }

  // if token present, Attach Authorization header 
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const finalOptions = {
    // send cookies
    credentials: 'include',
    ...options,
    headers
  };

  return fetch(url, finalOptions);
}
