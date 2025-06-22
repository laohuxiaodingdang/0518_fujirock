/**
 * 认证表单组件 - 登录和注册
 * 提供用户友好的登录/注册界面
 */
'use client'

import { useState } from 'react'
import { useAuth } from '@/hooks/useAuth'

// 表单模式
type AuthMode = 'login' | 'register'

interface AuthFormProps {
  mode?: AuthMode
  onSuccess?: () => void
  onModeChange?: (mode: AuthMode) => void
}

export default function AuthForm({ 
  mode = 'login', 
  onSuccess, 
  onModeChange 
}: AuthFormProps) {
  // 认证Hook
  const { signIn, signUp, loading } = useAuth()
  
  // 表单状态
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: ''
  })
  
  // UI状态
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  /**
   * 处理表单输入变化
   */
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
    
    // 清除错误信息
    if (error) setError(null)
  }

  /**
   * 验证表单数据
   */
  const validateForm = (): boolean => {
    if (!formData.email.trim()) {
      setError('请输入邮箱地址')
      return false
    }
    
    if (!formData.email.includes('@')) {
      setError('请输入有效的邮箱地址')
      return false
    }
    
    if (!formData.password.trim()) {
      setError('请输入密码')
      return false
    }
    
    if (formData.password.length < 6) {
      setError('密码至少需要6个字符')
      return false
    }
    
    if (mode === 'register' && formData.password !== formData.confirmPassword) {
      setError('两次输入的密码不一致')
      return false
    }
    
    return true
  }

  /**
   * 处理表单提交
   */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    // 验证表单
    if (!validateForm()) return
    
    setIsSubmitting(true)
    setError(null)
    setSuccess(null)
    
    try {
      let result
      
      if (mode === 'login') {
        // 登录
        result = await signIn(formData.email, formData.password)
        
        if (result.success) {
          setSuccess('登录成功！')
          onSuccess?.()
        } else {
          setError(result.error || '登录失败')
        }
      } else {
        // 注册
        result = await signUp(formData.email, formData.password)
        
        if (result.success) {
          setSuccess('注册成功！请检查邮箱并点击验证链接。')
          // 可以选择自动切换到登录模式
          // onModeChange?.('login')
        } else {
          setError(result.error || '注册失败')
        }
      }
    } catch (error) {
      console.error('Auth error:', error)
      setError('操作失败，请稍后重试')
    } finally {
      setIsSubmitting(false)
    }
  }

  /**
   * 切换表单模式
   */
  const toggleMode = () => {
    const newMode = mode === 'login' ? 'register' : 'login'
    onModeChange?.(newMode)
    
    // 清除表单状态
    setFormData({
      email: '',
      password: '',
      confirmPassword: ''
    })
    setError(null)
    setSuccess(null)
  }

  return (
    <div className="max-w-md mx-auto bg-white rounded-lg shadow-md p-6">
      {/* 标题 */}
      <h2 className="text-2xl font-bold text-center mb-6 text-gray-800">
        {mode === 'login' ? '用户登录' : '用户注册'}
      </h2>
      
      {/* 成功消息 */}
      {success && (
        <div className="mb-4 p-3 bg-green-100 border border-green-400 text-green-700 rounded">
          {success}
        </div>
      )}
      
      {/* 错误消息 */}
      {error && (
        <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}
      
      {/* 表单 */}
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* 邮箱输入 */}
        <div>
          <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
            邮箱地址
          </label>
          <input
            type="email"
            id="email"
            name="email"
            value={formData.email}
            onChange={handleInputChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="请输入邮箱地址"
            required
          />
        </div>
        
        {/* 密码输入 */}
        <div>
          <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
            密码
          </label>
          <input
            type="password"
            id="password"
            name="password"
            value={formData.password}
            onChange={handleInputChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="请输入密码（至少6个字符）"
            required
            minLength={6}
          />
        </div>
        
        {/* 确认密码输入（仅注册时显示） */}
        {mode === 'register' && (
          <div>
            <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-1">
              确认密码
            </label>
            <input
              type="password"
              id="confirmPassword"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="请再次输入密码"
              required
            />
          </div>
        )}
        
        {/* 提交按钮 */}
        <button
          type="submit"
          disabled={isSubmitting || loading}
          className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {isSubmitting ? (
            <span className="flex items-center justify-center">
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {mode === 'login' ? '登录中...' : '注册中...'}
            </span>
          ) : (
            mode === 'login' ? '登录' : '注册'
          )}
        </button>
      </form>
      
      {/* 模式切换 */}
      <div className="mt-6 text-center">
        <p className="text-sm text-gray-600">
          {mode === 'login' ? '还没有账号？' : '已有账号？'}
          <button
            type="button"
            onClick={toggleMode}
            className="ml-1 text-blue-600 hover:text-blue-800 font-medium"
          >
            {mode === 'login' ? '立即注册' : '立即登录'}
          </button>
        </p>
      </div>
    </div>
  )
} 