import { NextResponse } from 'next/server';

// 强制动态渲染，防止构建时静态生成
export const dynamic = 'force-dynamic';

// 简单的模拟数据响应
export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const query = searchParams.get('q') || 'radiohead';
    
    // 返回模拟数据
    return NextResponse.json({
      artists: {
        items: [
          {
            id: "4Z8W4fKeB5YxbusRsdQVPb",
            name: "Radiohead",
            images: [{ url: "https://i.scdn.co/image/ab67616d00001e02de3c04b5fc450d009178dd67" }],
            genres: ["alternative rock", "art rock", "melancholia", "permanent wave", "rock"],
            popularity: 82
          }
        ]
      }
    });
  } catch (error) {
    console.error('API error:', error);
    return NextResponse.json(
      { error: 'API test error' }, 
      { status: 500 }
    );
  }
}