// API服务封装

/**
 * API 客户端
 * 自动处理JWT Token认证的HTTP客户端
 */
import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { getCurrentUserToken } from './supabase'

// API基础URL - 根据环境变量设置
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

/**
 * 创建带有认证功能的API客户端
 */
class ApiClient {
  private client: AxiosInstance

  constructor() {
    // 创建axios实例
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 10000, // 10秒超时
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // 请求拦截器：自动添加JWT Token
    this.client.interceptors.request.use(
      async (config) => {
        try {
          // 获取当前用户的JWT Token
          const token = await getCurrentUserToken()
          
          if (token) {
            // 在请求头中添加Authorization字段
            config.headers.Authorization = `Bearer ${token}`
            console.log('🔐 Added JWT token to request:', config.url)
          } else {
            console.log('📝 No token available for request:', config.url)
          }
        } catch (error) {
          console.error('Error getting token for request:', error)
        }
        
        return config
      },
      (error) => {
        console.error('Request interceptor error:', error)
        return Promise.reject(error)
      }
    )

    // 响应拦截器：处理认证错误
    this.client.interceptors.response.use(
      (response) => {
        // 成功响应直接返回
        return response
      },
      async (error) => {
        // 处理401未授权错误
        if (error.response?.status === 401) {
          console.warn('🚫 Authentication failed:', error.response.data)
          
          // 可以在这里触发重新登录流程
          // 例如：跳转到登录页面或显示登录弹窗
          if (typeof window !== 'undefined') {
            // 只在浏览器环境中执行
            console.log('Redirecting to login due to 401 error')
            // window.location.href = '/login' // 可以取消注释来自动跳转
          }
        }
        
        return Promise.reject(error)
      }
    )
  }

  /**
   * GET 请求
   */
  async get<T = any>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return this.client.get<T>(url, config)
  }

  /**
   * POST 请求
   */
  async post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return this.client.post<T>(url, data, config)
  }

  /**
   * PUT 请求
   */
  async put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return this.client.put<T>(url, data, config)
  }

  /**
   * DELETE 请求
   */
  async delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return this.client.delete<T>(url, config)
  }

  /**
   * 不带认证的请求（用于公开API）
   */
  async publicGet<T = any>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    // 创建一个不带认证的临时客户端
    const publicClient = axios.create({
      baseURL: API_BASE_URL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    })
    
    return publicClient.get<T>(url, config)
  }
}

// 创建全局API客户端实例
export const apiClient = new ApiClient()

// ==================== 认证相关的API方法 ====================

/**
 * 验证当前Token是否有效
 */
export const verifyToken = async () => {
  try {
    const response = await apiClient.get('/api/auth/verify')
    return response.data
  } catch (error) {
    console.error('Token verification failed:', error)
    throw error
  }
}

/**
 * 获取用户资料
 */
export const getUserProfile = async () => {
  try {
    const response = await apiClient.get('/api/auth/profile')
    return response.data
  } catch (error) {
    console.error('Get user profile failed:', error)
    throw error
  }
}

/**
 * 用户登出（服务端记录）
 */
export const logoutUser = async () => {
  try {
    const response = await apiClient.post('/api/auth/logout')
    return response.data
  } catch (error) {
    console.error('Logout failed:', error)
    throw error
  }
}

// ==================== 需要认证的API示例 ====================

/**
 * 获取用户收藏的艺术家
 */
export const getUserFavorites = async () => {
  try {
    const response = await apiClient.get('/api/protected/user-favorites')
    return response.data
  } catch (error) {
    console.error('Get user favorites failed:', error)
    throw error
  }
}

/**
 * 添加艺术家到收藏
 */
export const addToFavorites = async (artistId: number) => {
  try {
    const response = await apiClient.post('/api/protected/add-favorite', { artist_id: artistId })
    return response.data
  } catch (error) {
    console.error('Add to favorites failed:', error)
    throw error
  }
}

/**
 * 获取公开内容（带可选认证）
 */
export const getPublicContent = async () => {
  try {
    const response = await apiClient.get('/api/protected/public-with-user-context')
    return response.data
  } catch (error) {
    console.error('Get public content failed:', error)
    throw error
  }
}

// ==================== 公开API示例 ====================

/**
 * 获取艺术家列表（不需要认证）
 */
export const getArtists = async () => {
  try {
    const response = await apiClient.publicGet('/api/database/artists')
    return response.data
  } catch (error) {
    console.error('Get artists failed:', error)
    throw error
  }
}

/**
 * 搜索艺术家
 */
export async function searchArtists(query: string) {
  try {
    const response = await fetch(`/api/spotify/search?q=${encodeURIComponent(query)}`);
    if (!response.ok) throw new Error('搜索失败');
    return await response.json();
  } catch (error) {
    console.error('搜索艺术家失败:', error);
    throw error;
  }
}

/**
 * 获取艺术家详情
 */
export async function getArtistDetails(id: string) {
  try {
    const response = await fetch(`/api/spotify/artist/${id}`);
    if (!response.ok) throw new Error('获取艺术家详情失败');
    return await response.json();
  } catch (error) {
    console.error('获取艺术家详情失败:', error);
    throw error;
  }
}

/**
 * 获取艺术家维基百科信息
 */
export async function getArtistWikipedia(name: string) {
  try {
    const response = await fetch(`/api/wikipedia?name=${encodeURIComponent(name)}`);
    if (!response.ok) throw new Error('获取维基百科信息失败');
    return await response.json();
  } catch (error) {
    console.error('获取维基百科信息失败:', error);
    throw error;
  }
}

/**
 * 获取艺术家赛博朋克风格描述
 */
export async function getArtistDescription(name: string, genre?: string) {
  try {
    let url = `/api/description?name=${encodeURIComponent(name)}`;
    if (genre) url += `&genre=${encodeURIComponent(genre)}`;
    
    const response = await fetch(url);
    if (!response.ok) throw new Error('获取艺术家描述失败');
    return await response.json();
  } catch (error) {
    console.error('获取艺术家描述失败:', error);
    throw error;
  }
} 