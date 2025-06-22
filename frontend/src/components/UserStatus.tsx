/**
 * 用户状态组件 - 显示登录状态和用户信息
 * 提供登出功能和用户信息展示
 */
'use client'

import { useState } from 'react'
import { useAuth } from '@/hooks/useAuth'
import { verifyToken, getUserProfile, logoutUser } from '@/lib/api'

interface UserStatusProps {
  className?: string
}

export default function UserStatus({ className = '' }: UserStatusProps) {
  // 认证Hook
  const { user, loading, isAuthenticated, signOut, token } = useAuth()
  
  // UI状态
  const [isLoggingOut, setIsLoggingOut] = useState(false)
  const [showDropdown, setShowDropdown] = useState(false)
  const [testResult, setTestResult] = useState<string | null>(null)

  /**
   * 处理登出
   */
  const handleSignOut = async () => {
    setIsLoggingOut(true)
    
    try {
      // 先调用后端登出API（记录登出日志）
      try {
        await logoutUser()
      } catch (error) {
        console.warn('Backend logout failed:', error)
        // 即使后端登出失败，也继续前端登出
      }
      
      // 前端登出（清除本地session）
      const result = await signOut()
      
      if (result.success) {
        console.log('用户已登出')
      } else {
        console.error('登出失败:', result.error)
      }
    } catch (error) {
      console.error('登出过程中出错:', error)
    } finally {
      setIsLoggingOut(false)
      setShowDropdown(false)
    }
  }

  /**
   * 测试Token验证
   */
  const testTokenVerification = async () => {
    try {
      setTestResult('验证中...')
      const result = await verifyToken()
      setTestResult(`✅ Token有效: ${result.user.email}`)
    } catch (error) {
      setTestResult(`❌ Token验证失败: ${error}`)
    }
  }

  /**
   * 测试获取用户资料
   */
  const testGetProfile = async () => {
    try {
      setTestResult('获取中...')
      const result = await getUserProfile()
      setTestResult(`✅ 用户资料: ${JSON.stringify(result.user, null, 2)}`)
    } catch (error) {
      setTestResult(`❌ 获取用户资料失败: ${error}`)
    }
  }

  // 加载中状态
  if (loading) {
    return (
      <div className={`flex items-center space-x-2 ${className}`}>
        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
        <span className="text-sm text-gray-600">加载中...</span>
      </div>
    )
  }

  // 未登录状态
  if (!isAuthenticated || !user) {
    return (
      <div className={`text-sm text-gray-600 ${className}`}>
        <span>未登录</span>
      </div>
    )
  }

  // 已登录状态
  return (
    <div className={`relative ${className}`}>
      {/* 用户信息显示 */}
      <div className="flex items-center space-x-3">
        {/* 用户头像 */}
        <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
          <span className="text-white text-sm font-medium">
            {user.email?.[0]?.toUpperCase() || 'U'}
          </span>
        </div>
        
        {/* 用户邮箱和下拉按钮 */}
        <div className="flex items-center space-x-1">
          <span className="text-sm font-medium text-gray-800">
            {user.email}
          </span>
          <button
            onClick={() => setShowDropdown(!showDropdown)}
            className="text-gray-500 hover:text-gray-700 focus:outline-none"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>
        </div>
      </div>

      {/* 下拉菜单 */}
      {showDropdown && (
        <div className="absolute right-0 mt-2 w-80 bg-white rounded-md shadow-lg border border-gray-200 z-50">
          <div className="py-2">
            {/* 用户信息 */}
            <div className="px-4 py-2 border-b border-gray-100">
              <p className="text-sm font-medium text-gray-800">{user.email}</p>
              <p className="text-xs text-gray-500">用户ID: {user.id}</p>
              {token && (
                <p className="text-xs text-gray-500 mt-1">
                  Token: {token.substring(0, 20)}...
                </p>
              )}
            </div>
            
            {/* 测试功能 */}
            <div className="px-4 py-2 border-b border-gray-100">
              <p className="text-xs font-medium text-gray-600 mb-2">API测试功能：</p>
              <div className="space-y-1">
                <button
                  onClick={testTokenVerification}
                  className="block w-full text-left text-xs text-blue-600 hover:text-blue-800"
                >
                  🔍 测试Token验证
                </button>
                <button
                  onClick={testGetProfile}
                  className="block w-full text-left text-xs text-blue-600 hover:text-blue-800"
                >
                  👤 测试获取用户资料
                </button>
              </div>
              
              {/* 测试结果 */}
              {testResult && (
                <div className="mt-2 p-2 bg-gray-50 rounded text-xs">
                  <pre className="whitespace-pre-wrap">{testResult}</pre>
                </div>
              )}
            </div>
            
            {/* 登出按钮 */}
            <div className="px-4 py-2">
              <button
                onClick={handleSignOut}
                disabled={isLoggingOut}
                className="w-full text-left text-sm text-red-600 hover:text-red-800 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoggingOut ? (
                  <span className="flex items-center">
                    <svg className="animate-spin -ml-1 mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    登出中...
                  </span>
                ) : (
                  '🚪 登出'
                )}
              </button>
            </div>
          </div>
        </div>
      )}
      
      {/* 点击外部关闭下拉菜单 */}
      {showDropdown && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setShowDropdown(false)}
        />
      )}
    </div>
  )
} 