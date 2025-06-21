// src/services/api.js
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to automatically add token
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }
    return config;
  },
  error => Promise.reject(error)
);

// API functions
export const authAPI = {
  login: (username, password) => 
    api.post('/login/', { username, password }),
  
  register: (userData) => 
    api.post('/register/', userData),
  
  logout: () => 
    api.post('/logout/'),
};

export const restroomAPI = {
  getList: () => 
    api.get('/restrooms/'),
  
  getDetail: (id) => 
    api.get(`/restrooms/${id}/`),
  
  create: (data) => 
    api.post('/restrooms/', data),
  
  update: (id, data) => 
    api.put(`/restrooms/${id}/`, data),
  
  delete: (id) => 
    api.delete(`/restrooms/${id}/`),
};

export const reviewAPI = {
  getList: (restroomId = null) => {
    const url = restroomId ? `/reviews/?restroom_id=${restroomId}` : '/reviews/';
    return api.get(url);
  },
  
  create: (data) => 
    api.post('/reviews/', data),
};

export const productAPI = {
  getList: () => 
    api.get('/products/'),
};

export const orderAPI = {
  create: (data) => 
    api.post('/orders/', data),
  
  getMyOrders: () => 
    api.get('/orders/my/'),
};

export const userAPI = {
  getProfile: () => 
    api.get('/profile/'),
  
  updateProfile: (data) => 
    api.put('/profile/update/', data),
};