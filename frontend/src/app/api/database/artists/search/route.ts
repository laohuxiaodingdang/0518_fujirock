import { NextRequest, NextResponse } from 'next/server';

// 强制动态渲染，防止构建时静态生成
export const dynamic = 'force-dynamic';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const name = searchParams.get('name') || '';
    const query = searchParams.get('query') || '';
    const limit = parseInt(searchParams.get('limit') || '10');
    const offset = parseInt(searchParams.get('offset') || '0');

    // 如果是按名称搜索 Fred again..
    if (name) {
      // 调用后端 API - 使用 v1 前缀
      const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      console.log(backendUrl);
      const response = await fetch(
        `${backendUrl}/api/database/artists?query=${encodeURIComponent(name)}&limit=1`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      if (!response.ok) {
        console.error(`Backend API error: ${response.status}`);
        const errorText = await response.text();
        console.error('Error details:', errorText);
        throw new Error(`Backend API error: ${response.status}`);
      }

      const data = await response.json();
      
      // 返回单个艺术家数据
      if (data.success && data.data && data.data.length > 0) {
        return NextResponse.json({
          success: true,
          artist: data.data[0]
        });
      } else {
        return NextResponse.json({
          success: false,
          error: 'Artist not found'
        }, { status: 404 });
      }
    }

    // 原有的查询逻辑 - 使用 v1 前缀
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const response = await fetch(
      `${backendUrl}/api/database/artists?query=${encodeURIComponent(query)}&limit=${limit}&offset=${offset}`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    if (!response.ok) {
      console.error(`Backend API error: ${response.status}`);
      const errorText = await response.text();
      console.error('Error details:', errorText);
      throw new Error(`Backend API error: ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data);

  } catch (error) {
    console.error('API Error:', error);
    return NextResponse.json(
      { 
        success: false, 
        error: 'Failed to search artists',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
} 