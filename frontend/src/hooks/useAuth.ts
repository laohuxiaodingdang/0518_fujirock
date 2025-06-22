/**
 * 认证相关的React Hook
 * 提供登录、注册、登出等功能
 */
import { useState, useEffect } from 'react'
import { User, AuthError } from '@supabase/supabase-js'
import { supabase, getCurrentUserToken } from '@/lib/supabase'

// 认证状态接口
interface AuthState {
  user: User | null
  loading: boolean
  token: string | null
}

// 认证操作结果接口
interface AuthResult {
  success: boolean
  error?: string
}

/**
 * 认证Hook
 * 管理用户的登录状态和认证操作
 */
export function useAuth() {
  // 认证状态
  const [authState, setAuthState] = useState<AuthState>({
    user: null,
    loading: true,
    token: null
  })

  /**
   * 初始化认证状态
   * 检查用户是否已经登录
   */
  useEffect(() => {
    // 获取初始session
    const getInitialSession = async () => {
      try {
        const { data: { session }, error } = await supabase.auth.getSession()
        
        if (error) {
          console.error('Error getting initial session:', error)
        }
        
        setAuthState({
          user: session?.user || null,
          loading: false,
          token: session?.access_token || null
        })
      } catch (error) {
        console.error('Error in getInitialSession:', error)
        setAuthState({
          user: null,
          loading: false,
          token: null
        })
      }
    }

    getInitialSession()

    // 监听认证状态变化
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event, session) => {
        console.log('Auth state changed:', event, session?.user?.email)
        
        setAuthState({
          user: session?.user || null,
          loading: false,
          token: session?.access_token || null
        })
      }
    )

    // 清理订阅
    return () => subscription.unsubscribe()
  }, [])

  /**
   * 用户注册
   * 
   * @param email 邮箱地址
   * @param password 密码
   * @returns Promise<AuthResult> 注册结果
   */
  const signUp = async (email: string, password: string): Promise<AuthResult> => {
    try {
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
      })

      if (error) {
        return {
          success: false,
          error: error.message
        }
      }

      // 注册成功
      return {
        success: true
      }
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred'
      }
    }
  }

  /**
   * 用户登录
   * 
   * @param email 邮箱地址
   * @param password 密码
   * @returns Promise<AuthResult> 登录结果
   */
  const signIn = async (email: string, password: string): Promise<AuthResult> => {
    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password,
      })

      if (error) {
        return {
          success: false,
          error: error.message
        }
      }

      // 登录成功，状态会通过onAuthStateChange自动更新
      return {
        success: true
      }
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred'
      }
    }
  }

  /**
   * 用户登出
   * 
   * @returns Promise<AuthResult> 登出结果
   */
  const signOut = async (): Promise<AuthResult> => {
    try {
      const { error } = await supabase.auth.signOut()

      if (error) {
        return {
          success: false,
          error: error.message
        }
      }

      // 登出成功，状态会通过onAuthStateChange自动更新
      return {
        success: true
      }
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred'
      }
    }
  }

  /**
   * 刷新当前用户的Token
   * 
   * @returns Promise<string | null> 新的Token或null
   */
  const refreshToken = async (): Promise<string | null> => {
    try {
      const { data, error } = await supabase.auth.refreshSession()
      
      if (error) {
        console.error('Error refreshing token:', error)
        return null
      }
      
      const newToken = data.session?.access_token || null
      
      // 更新状态
      setAuthState(prev => ({
        ...prev,
        token: newToken,
        user: data.session?.user || prev.user
      }))
      
      return newToken
    } catch (error) {
      console.error('Error in refreshToken:', error)
      return null
    }
  }

  return {
    // 状态
    user: authState.user,
    loading: authState.loading,
    token: authState.token,
    isAuthenticated: !!authState.user,
    
    // 操作
    signUp,
    signIn,
    signOut,
    refreshToken
  }
} 