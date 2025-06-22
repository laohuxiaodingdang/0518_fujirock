import './globals.css';
import type { Metadata } from 'next';
import { Inter, Orbitron } from 'next/font/google';

const inter = Inter({ 
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
});

const orbitron = Orbitron({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-orbitron',
});

export const metadata: Metadata = {
  metadataBase: new URL(process.env.FRONTEND_URL || 'http://localhost:3000'),
  title: 'Fuji Rock 2025 音乐探索工具',
  description: '探索即将在 Fuji Rock 2025 演出的艺术家，发现新音乐',
  keywords: ['Fuji Rock', '2025', '音乐节', '艺术家', 'Fred again', '音乐探索'],
  authors: [{ name: 'Fuji Rock 2025' }],
  icons: {
    icon: [
      { url: '/favicon.ico', sizes: 'any' },
      { url: '/favicon.ico', type: 'image/x-icon' },
    ],
    apple: [
      { url: '/favicon.ico', sizes: '180x180' },
    ],
  },
  manifest: '/site.webmanifest',
  viewport: 'width=device-width, initial-scale=1',
  themeColor: '#6366f1',
  openGraph: {
    title: 'Fuji Rock 2025 音乐探索工具',
    description: '探索即将在 Fuji Rock 2025 演出的艺术家，发现新音乐',
    type: 'website',
    locale: 'zh_CN',
    siteName: 'Fuji Rock 2025',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Fuji Rock 2025 音乐探索工具',
    description: '探索即将在 Fuji Rock 2025 演出的艺术家，发现新音乐',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-CN">
      <head>
        <link rel="icon" href="/favicon.ico" sizes="any" />
        <link rel="icon" href="/favicon.ico" type="image/x-icon" />
        <link rel="apple-touch-icon" href="/favicon.ico" />
      </head>
      <body className={`${inter.variable} ${orbitron.variable} font-sans`}>
        {children}
      </body>
    </html>
  );
} 