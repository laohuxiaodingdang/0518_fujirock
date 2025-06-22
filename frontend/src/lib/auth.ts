import { supabase, isSupabaseAvailable } from './supabase'
import type { User, AuthError } from '@supabase/supabase-js'

export interface AuthResult {
  user?: User | null
  error?: AuthError | null
}

export const authService = {
  /**
   * 用户注册
   */
  async signUp(email: string, password: string): Promise<AuthResult> {
    if (!isSupabaseAvailable || !supabase) {
      return { error: new Error('Authentication service not available') as AuthError }
    }

    try {
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          // 跳过邮箱验证，简化流程
          emailRedirectTo: undefined
        }
      })
      
      if (error) {
        console.error('注册失败:', error.message)
        return { error }
      }
      
      console.log('注册成功:', data.user?.email)
      return { user: data.user }
    } catch (err) {
      console.error('注册异常:', err)
      return { error: err as AuthError }
    }
  },

  /**
   * 用户登录
   */
  async signIn(email: string, password: string): Promise<AuthResult> {
    if (!isSupabaseAvailable || !supabase) {
      return { error: new Error('Authentication service not available') as AuthError }
    }

    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password
      })
      
      if (error) {
        console.error('登录失败:', error.message)
        return { error }
      }
      
      console.log('登录成功:', data.user?.email)
      return { user: data.user }
    } catch (err) {
      console.error('登录异常:', err)
      return { error: err as AuthError }
    }
  },

  /**
   * 用户登出
   */
  async signOut(): Promise<{ error?: AuthError | null }> {
    if (!isSupabaseAvailable || !supabase) {
      return { error: new Error('Authentication service not available') as AuthError }
    }

    try {
      const { error } = await supabase.auth.signOut()
      
      if (error) {
        console.error('登出失败:', error.message)
        return { error }
      }
      
      console.log('登出成功')
      return {}
    } catch (err) {
      console.error('登出异常:', err)
      return { error: err as AuthError }
    }
  },

  /**
   * 获取当前用户
   */
  async getCurrentUser(): Promise<User | null> {
    if (!isSupabaseAvailable || !supabase) {
      return null
    }

    try {
      const { data: { user }, error } = await supabase.auth.getUser()
      
      if (error) {
        console.error('获取用户信息失败:', error.message)
        return null
      }
      
      return user
    } catch (err) {
      console.error('获取用户信息异常:', err)
      return null
    }
  },

  /**
   * 监听认证状态变化
   */
  onAuthStateChange(callback: (user: User | null) => void) {
    if (!isSupabaseAvailable || !supabase) {
      // 如果 Supabase 不可用，返回一个空的订阅对象
      return { unsubscribe: () => {} }
    }

    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      (event, session) => {
        console.log('认证状态变化:', event, session?.user?.email || 'no user')
        callback(session?.user || null)
      }
    )
    
    return subscription
  },

  /**
   * 检查用户是否已登录
   */
  async isLoggedIn(): Promise<boolean> {
    const user = await this.getCurrentUser()
    return !!user
  }
} 