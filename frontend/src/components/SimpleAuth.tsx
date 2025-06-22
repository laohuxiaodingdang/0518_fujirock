'use client'

import { useState } from 'react'
import { authService } from '../lib/auth'

interface SimpleAuthProps {
  onSuccess?: () => void
  onClose?: () => void
}

export default function SimpleAuth({ onSuccess, onClose }: SimpleAuthProps) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [isLogin, setIsLogin] = useState(true)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    // 简单的表单验证
    if (!email || !password) {
      setError('请填写邮箱和密码')
      setLoading(false)
      return
    }

    if (password.length < 6) {
      setError('密码至少需要6位')
      setLoading(false)
      return
    }

    try {
      let result
      if (isLogin) {
        result = await authService.signIn(email, password)
      } else {
        result = await authService.signUp(email, password)
      }

      if (result.error) {
        // 处理常见错误信息
        const errorMessage = result.error.message
        if (errorMessage.includes('Invalid login credentials')) {
          setError('邮箱或密码错误')
        } else if (errorMessage.includes('User already registered')) {
          setError('该邮箱已注册，请直接登录')
        } else if (errorMessage.includes('Password should be at least 6 characters')) {
          setError('密码至少需要6位')
        } else {
          setError(errorMessage)
        }
      } else {
        // 成功
        console.log(isLogin ? '登录成功' : '注册成功')
        onSuccess?.()
      }
    } catch (err) {
      console.error('认证异常:', err)
      setError('网络错误，请稍后重试')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl p-6 w-full max-w-md mx-4">
        {/* 关闭按钮 */}
        {onClose && (
          <button
            onClick={onClose}
            className="float-right text-gray-400 hover:text-gray-600 text-xl"
          >
            ×
          </button>
        )}

        <h2 className="text-2xl font-bold mb-6 text-center text-gray-800">
          {isLogin ? '登录收藏音乐' : '注册新账号'}
        </h2>

        {error && (
          <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
              邮箱
            </label>
            <input
              id="email"
              type="email"
              placeholder="请输入邮箱"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
              disabled={loading}
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
              密码
            </label>
            <input
              id="password"
              type="password"
              placeholder="请输入密码（至少6位）"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
              disabled={loading}
              minLength={6}
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-500 text-white p-3 rounded-lg hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? '处理中...' : (isLogin ? '登录' : '注册')}
          </button>
        </form>

        <div className="mt-6 text-center">
          <p className="text-gray-600">
            {isLogin ? '还没有账号？' : '已有账号？'}
            <button
              onClick={() => {
                setIsLogin(!isLogin)
                setError('')
              }}
              className="text-blue-500 hover:text-blue-600 ml-1 font-medium"
              disabled={loading}
            >
              {isLogin ? '立即注册' : '立即登录'}
            </button>
          </p>
        </div>

        {!isLogin && (
          <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-sm text-blue-700">
              💡 注册后即可收藏喜欢的艺术家，数据会自动同步到云端
            </p>
          </div>
        )}
      </div>
    </div>
  )
} 