/**
 * 认证功能演示页面
 * 展示完整的认证流程和API调用
 */
'use client'

import { useState } from 'react'
import AuthForm from '@/components/AuthForm'
import UserStatus from '@/components/UserStatus'
import { useAuth } from '@/hooks/useAuth'
import { 
  getUserFavorites, 
  addToFavorites, 
  getPublicContent, 
  getArtists 
} from '@/lib/api'
import { isSupabaseAvailable } from '@/lib/supabase'

export default function AuthDemoPage() {
  const { 
    user, 
    loading, 
    isAuthenticated, 
    signUp, 
    signIn, 
    signOut,
    isSupabaseAvailable: supabaseAvailable
  } = useAuth()
  
  // UI状态
  const [authMode, setAuthMode] = useState<'login' | 'register'>('login')
  const [apiResults, setApiResults] = useState<Record<string, any>>({})
  const [isTestingApi, setIsTestingApi] = useState<string | null>(null)

  /**
   * 测试API调用
   */
  const testApi = async (apiName: string, apiFunction: () => Promise<any>) => {
    setIsTestingApi(apiName)
    
    try {
      const result = await apiFunction()
      setApiResults(prev => ({
        ...prev,
        [apiName]: {
          success: true,
          data: result,
          timestamp: new Date().toLocaleTimeString()
        }
      }))
    } catch (error) {
      setApiResults(prev => ({
        ...prev,
        [apiName]: {
          success: false,
          error: error instanceof Error ? error.message : String(error),
          timestamp: new Date().toLocaleTimeString()
        }
      }))
    } finally {
      setIsTestingApi(null)
    }
  }

  /**
   * 清除测试结果
   */
  const clearResults = () => {
    setApiResults({})
  }

  // 如果 Supabase 不可用，显示提示信息
  if (!isSupabaseAvailable) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-pink-900">
        <div className="container mx-auto px-4 py-8">
          <div className="max-w-4xl mx-auto">
            <div className="text-center mb-8">
              <h1 className="text-4xl font-bold text-white mb-4">
                🔐 Supabase 认证功能演示
              </h1>
              <p className="text-gray-300 text-lg">
                认证服务当前不可用
              </p>
            </div>

            <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 border border-white/20">
              <div className="text-center">
                <div className="text-6xl mb-4">⚠️</div>
                <h2 className="text-2xl font-bold text-white mb-4">认证服务不可用</h2>
                <p className="text-gray-300 mb-6">
                  Supabase 环境变量未配置，认证功能已禁用。
                </p>
                <div className="bg-yellow-500/20 border border-yellow-500/30 rounded-lg p-4 mb-6">
                  <p className="text-yellow-200 text-sm">
                    <strong>开发者提示：</strong> 请在部署环境中配置以下环境变量：
                  </p>
                  <ul className="text-yellow-200 text-sm mt-2 text-left list-disc list-inside">
                    <li>NEXT_PUBLIC_SUPABASE_URL</li>
                    <li>NEXT_PUBLIC_SUPABASE_ANON_KEY</li>
                  </ul>
                </div>
                <button
                  onClick={() => window.history.back()}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg transition-colors"
                >
                  返回上一页
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        {/* 页面标题 */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            🔐 Supabase 认证功能演示
          </h1>
          <p className="text-gray-600">
            完整的JWT认证流程：注册 → 登录 → API调用 → 登出
          </p>
        </div>

        {/* 用户状态栏 */}
        <div className="bg-white rounded-lg shadow-md p-4 mb-6">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-800">当前用户状态</h2>
            <UserStatus />
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* 左侧：认证表单 */}
          <div className="space-y-6">
            {!isAuthenticated ? (
              <div>
                <h2 className="text-xl font-semibold text-gray-800 mb-4">
                  步骤 1: 用户认证
                </h2>
                <AuthForm 
                  mode={authMode}
                  onModeChange={setAuthMode}
                  onSuccess={() => {
                    console.log('认证成功！')
                  }}
                />
              </div>
            ) : (
              <div className="bg-green-50 border border-green-200 rounded-lg p-6">
                <h2 className="text-xl font-semibold text-green-800 mb-2">
                  ✅ 认证成功！
                </h2>
                <p className="text-green-700">
                  您已成功登录，现在可以测试需要认证的API接口。
                </p>
              </div>
            )}

            {/* API测试功能 */}
            {isAuthenticated && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-xl font-semibold text-gray-800">
                    步骤 2: API 测试
                  </h2>
                  <button
                    onClick={clearResults}
                    className="text-sm text-gray-500 hover:text-gray-700"
                  >
                    清除结果
                  </button>
                </div>
                
                <div className="space-y-3">
                  {/* 需要认证的API */}
                  <div>
                    <h3 className="text-sm font-medium text-gray-700 mb-2">
                      🔒 需要认证的API：
                    </h3>
                    <div className="space-y-2">
                      <button
                        onClick={() => testApi('getUserFavorites', getUserFavorites)}
                        disabled={isTestingApi === 'getUserFavorites'}
                        className="w-full text-left p-2 text-sm bg-blue-50 hover:bg-blue-100 rounded border border-blue-200 disabled:opacity-50"
                      >
                        {isTestingApi === 'getUserFavorites' ? '🔄 测试中...' : '📋 获取用户收藏'}
                      </button>
                      
                      <button
                        onClick={() => testApi('addToFavorites', () => addToFavorites(1))}
                        disabled={isTestingApi === 'addToFavorites'}
                        className="w-full text-left p-2 text-sm bg-blue-50 hover:bg-blue-100 rounded border border-blue-200 disabled:opacity-50"
                      >
                        {isTestingApi === 'addToFavorites' ? '🔄 测试中...' : '❤️ 添加收藏 (艺术家ID: 1)'}
                      </button>
                    </div>
                  </div>

                  {/* 可选认证的API */}
                  <div>
                    <h3 className="text-sm font-medium text-gray-700 mb-2">
                      🔓 可选认证的API：
                    </h3>
                    <div className="space-y-2">
                      <button
                        onClick={() => testApi('getPublicContent', getPublicContent)}
                        disabled={isTestingApi === 'getPublicContent'}
                        className="w-full text-left p-2 text-sm bg-green-50 hover:bg-green-100 rounded border border-green-200 disabled:opacity-50"
                      >
                        {isTestingApi === 'getPublicContent' ? '🔄 测试中...' : '🌍 获取公开内容（带个性化）'}
                      </button>
                    </div>
                  </div>

                  {/* 公开API */}
                  <div>
                    <h3 className="text-sm font-medium text-gray-700 mb-2">
                      🌐 公开API（无需认证）：
                    </h3>
                    <div className="space-y-2">
                      <button
                        onClick={() => testApi('getArtists', getArtists)}
                        disabled={isTestingApi === 'getArtists'}
                        className="w-full text-left p-2 text-sm bg-gray-50 hover:bg-gray-100 rounded border border-gray-200 disabled:opacity-50"
                      >
                        {isTestingApi === 'getArtists' ? '🔄 测试中...' : '🎵 获取艺术家列表'}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* 右侧：测试结果 */}
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold text-gray-800 mb-4">
                🧪 API 测试结果
              </h2>
              
              {Object.keys(apiResults).length === 0 ? (
                <div className="text-gray-500 text-center py-8">
                  <p>还没有测试结果</p>
                  <p className="text-sm mt-1">登录后点击左侧的API测试按钮</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {Object.entries(apiResults).map(([apiName, result]) => (
                    <div key={apiName} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="font-medium text-gray-800">
                          {apiName}
                        </h3>
                        <div className="flex items-center space-x-2">
                          <span className={`text-xs px-2 py-1 rounded ${
                            result.success 
                              ? 'bg-green-100 text-green-800' 
                              : 'bg-red-100 text-red-800'
                          }`}>
                            {result.success ? '成功' : '失败'}
                          </span>
                          <span className="text-xs text-gray-500">
                            {result.timestamp}
                          </span>
                        </div>
                      </div>
                      
                      <div className="bg-gray-50 rounded p-3">
                        <pre className="text-xs text-gray-700 whitespace-pre-wrap overflow-x-auto">
                          {result.success 
                            ? JSON.stringify(result.data, null, 2)
                            : result.error
                          }
                        </pre>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* 使用说明 */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-blue-800 mb-3">
                💡 使用说明
              </h3>
              <div className="text-sm text-blue-700 space-y-2">
                <p><strong>1. 注册/登录：</strong> 使用邮箱和密码进行注册或登录</p>
                <p><strong>2. 自动认证：</strong> 登录后，所有API请求会自动携带JWT Token</p>
                <p><strong>3. 测试API：</strong> 点击测试按钮验证不同类型的API接口</p>
                <p><strong>4. 查看结果：</strong> 在右侧查看API调用的详细结果</p>
                <p><strong>5. 登出：</strong> 点击用户状态区域的登出按钮</p>
              </div>
            </div>

            {/* 技术说明 */}
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-yellow-800 mb-3">
                🔧 技术实现
              </h3>
              <div className="text-sm text-yellow-700 space-y-2">
                <p><strong>前端：</strong> Next.js + Supabase Auth + Axios</p>
                <p><strong>后端：</strong> FastAPI + PyJWT + Supabase JWT验证</p>
                <p><strong>认证流程：</strong> Supabase生成JWT → 前端自动携带 → 后端验证</p>
                <p><strong>Token管理：</strong> 自动刷新 + 本地存储 + 过期处理</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
} 