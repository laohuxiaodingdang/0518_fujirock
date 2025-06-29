import { NextRequest, NextResponse } from 'next/server';

// 强制动态渲染，防止构建时静态生成
export const dynamic = 'force-dynamic';

export async function GET(
  request: NextRequest,
  { params }: { params: { name: string } }
) {
  try {
    const artistName = decodeURIComponent(params.name);
    console.log('🔍 API Route - 搜索艺术家:', artistName);

    // 调用后端 API
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const apiUrl = `${backendUrl}/api/database/artists/by-name/${encodeURIComponent(artistName)}`;
    
    console.log('🌐 调用后端 API:', apiUrl);

    const response = await fetch(apiUrl, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    console.log('📊 后端响应状态:', response.status);

    if (!response.ok) {
      const errorText = await response.text();
      console.error('❌ 后端 API 错误:', response.status, errorText);
      throw new Error(`Backend API error: ${response.status}`);
    }

    const data = await response.json();
    console.log('✅ 后端返回数据:', data.success ? '成功' : '失败');
    
    if (data.success) {
      console.log('📝 艺术家数据包含 ai_description:', !!data.data?.ai_description);
    }

    return NextResponse.json(data);

  } catch (error) {
    console.error('❌ API Route 错误:', error);
    return NextResponse.json(
      { 
        success: false, 
        error: 'Failed to get artist by name',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}