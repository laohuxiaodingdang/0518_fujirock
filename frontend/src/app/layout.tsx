import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Fuji Rock Festival 2025',
  description: '🎪 Get ready for Fuji Rock 2025 - Discover amazing artists and stages',
  keywords: ['Fuji Rock', '2025', 'music festival', 'artists', 'Japan'],
  authors: [{ name: 'Fuji Rock 2025' }],
  // 优化移动端显示的viewport设置
  viewport: {
    width: 'device-width',
    initialScale: 1,
    maximumScale: 1,
    userScalable: false, // 防止用户缩放造成布局问题
  },
  themeColor: '#ff1493',
  icons: {
    icon: '/favicon.ico',
  },
  openGraph: {
    title: 'Fuji Rock Festival 2025',
    description: '🎪 Get ready for Fuji Rock 2025 - Discover amazing artists and stages',
    type: 'website',
    locale: 'en_US',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        {/* 移动端优化的meta标签 */}
        <meta name="format-detection" content="telephone=no" />
        <meta name="mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
        
        {/* Google Fonts - 直接加载需要的字体 */}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link 
          href="https://fonts.googleapis.com/css2?family=Rock+Salt&family=Audiowide&family=Orbitron:wght@400;500;700&family=Noto+Sans+SC:wght@100;200;300;400;500;600;700;800;900&display=swap" 
          rel="stylesheet" 
        />
      </head>
      <body>
        {children}
      </body>
    </html>
  );
}