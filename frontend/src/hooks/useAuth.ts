/**
 * 认证相关的React Hook
 * 提供登录、注册、登出等功能
 */
import { useState, useEffect, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { toast } from 'react-hot-toast'
import { User, AuthError } from '@supabase/supabase-js'
import { supabase, getCurrentUserToken, isSupabaseAvailable } from '@/lib/supabase'

// 认证状态接口
interface AuthState {
  user: User | null
  loading: boolean
  isAuthenticated: boolean
}

// 认证操作结果接口
interface AuthResult {
  success: boolean
  error?: string
}

interface SignUpData {
  email: string
  password: string
  name?: string
}

interface SignInData {
  email: string
  password: string
}

/**
 * 认证Hook
 * 管理用户的登录状态和认证操作
 */
export const useAuth = () => {
  const router = useRouter()
  const [authState, setAuthState] = useState<AuthState>({
    user: null,
    loading: true,
    isAuthenticated: false
  })

  // 获取当前用户信息
  const getCurrentUser = useCallback(async () => {
    if (!isSupabaseAvailable || !supabase) {
      setAuthState({
        user: null,
        loading: false,
        isAuthenticated: false
      })
      return
    }

    try {
      setAuthState(prev => ({ ...prev, loading: true }))
      
      const { data: { session }, error } = await supabase.auth.getSession()
      
      if (error) {
        console.error('Error getting session:', error)
        setAuthState({
          user: null,
          loading: false,
          isAuthenticated: false
        })
        return
      }
      
      setAuthState({
        user: session?.user || null,
        loading: false,
        isAuthenticated: !!session?.user
      })
    } catch (error) {
      console.error('Error in getCurrentUser:', error)
      setAuthState({
        user: null,
        loading: false,
        isAuthenticated: false
      })
    }
  }, [])

  // 监听认证状态变化
  useEffect(() => {
    if (!isSupabaseAvailable || !supabase) {
      setAuthState({
        user: null,
        loading: false,
        isAuthenticated: false
      })
      return
    }

    getCurrentUser()

    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event, session) => {
        console.log('Auth state changed:', event, session?.user?.email)
        
        setAuthState({
          user: session?.user || null,
          loading: false,
          isAuthenticated: !!session?.user
        })

        if (event === 'SIGNED_IN') {
          toast.success('登录成功！')
        } else if (event === 'SIGNED_OUT') {
          toast.success('已退出登录')
          router.push('/')
        }
      }
    )

    return () => {
      subscription.unsubscribe()
    }
  }, [getCurrentUser, router])

  // 注册用户
  const signUp = useCallback(async ({ email, password, name }: SignUpData) => {
    if (!isSupabaseAvailable || !supabase) {
      toast.error('认证服务不可用')
      return { user: null, error: new Error('Authentication service not available') as AuthError }
    }

    try {
      setAuthState(prev => ({ ...prev, loading: true }))
      
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: {
            name: name || email.split('@')[0]
          }
        }
      })

      if (error) {
        toast.error(`注册失败: ${error.message}`)
        return { user: null, error }
      }

      if (data.user && !data.session) {
        toast.success('注册成功！请检查邮箱验证链接。')
      } else if (data.session) {
        toast.success('注册并登录成功！')
      }

      return { user: data.user, error: null }
    } catch (error) {
      const authError = error as AuthError
      toast.error(`注册失败: ${authError.message}`)
      return { user: null, error: authError }
    } finally {
      setAuthState(prev => ({ ...prev, loading: false }))
    }
  }, [])

  // 登录用户
  const signIn = useCallback(async ({ email, password }: SignInData) => {
    if (!isSupabaseAvailable || !supabase) {
      toast.error('认证服务不可用')
      return { user: null, error: new Error('Authentication service not available') as AuthError }
    }

    try {
      setAuthState(prev => ({ ...prev, loading: true }))
      
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password
      })

      if (error) {
        toast.error(`登录失败: ${error.message}`)
        return { user: null, error }
      }

      // 成功登录的toast会在onAuthStateChange中处理
      return { user: data.user, error: null }
    } catch (error) {
      const authError = error as AuthError
      toast.error(`登录失败: ${authError.message}`)
      return { user: null, error: authError }
    } finally {
      setAuthState(prev => ({ ...prev, loading: false }))
    }
  }, [])

  // 退出登录
  const signOut = useCallback(async () => {
    if (!isSupabaseAvailable || !supabase) {
      // 即使 Supabase 不可用，也要清除本地状态
      setAuthState({
        user: null,
        loading: false,
        isAuthenticated: false
      })
      return { error: null }
    }

    try {
      setAuthState(prev => ({ ...prev, loading: true }))
      
      const { error } = await supabase.auth.signOut()
      
      if (error) {
        toast.error(`退出失败: ${error.message}`)
        return { error }
      }

      // 成功退出的toast会在onAuthStateChange中处理
      return { error: null }
    } catch (error) {
      const authError = error as AuthError
      toast.error(`退出失败: ${authError.message}`)
      return { error: authError }
    } finally {
      setAuthState(prev => ({ ...prev, loading: false }))
    }
  }, [])

  // 刷新会话
  const refreshSession = useCallback(async () => {
    if (!isSupabaseAvailable || !supabase) {
      return { session: null, error: new Error('Authentication service not available') as AuthError }
    }

    try {
      const { data, error } = await supabase.auth.refreshSession()
      
      if (error) {
        console.error('Error refreshing session:', error)
        return { session: null, error }
      }
      
      return { session: data.session, error: null }
    } catch (error) {
      const authError = error as AuthError
      console.error('Error in refreshSession:', authError)
      return { session: null, error: authError }
    }
  }, [])

  // 获取当前用户的JWT Token
  const getToken = useCallback(async () => {
    return await getCurrentUserToken()
  }, [])

  return {
    // 状态
    user: authState.user,
    loading: authState.loading,
    isAuthenticated: authState.isAuthenticated,
    isSupabaseAvailable,
    
    // 方法
    signUp,
    signIn,
    signOut,
    refreshSession,
    getToken,
    getCurrentUser
  }
} 