/**
 * 音乐平台服务 - 处理音乐平台URL的生成和管理
 */

/**
 * 生成QQ音乐搜索链接
 */
export function generateQQMusicSearchUrl(artistName: string): string {
  return `https://y.qq.com/n/ryqq/search?w=${encodeURIComponent(artistName)}`;
}

/**
 * 生成网易云音乐搜索链接
 */
export function generateNeteaseSearchUrl(artistName: string): string {
  return `https://music.163.com/#/search/m/?s=${encodeURIComponent(artistName)}`;
}

/**
 * 生成Apple Music搜索链接
 */
export function generateAppleMusicSearchUrl(artistName: string): string {
  return `https://music.apple.com/search?term=${encodeURIComponent(artistName)}`;
}

/**
 * 生成YouTube Music搜索链接
 */
export function generateYouTubeMusicSearchUrl(artistName: string): string {
  return `https://music.youtube.com/search?q=${encodeURIComponent(artistName)}`;
}

/**
 * 生成KKBOX搜索链接
 */
export function generateKKBOXSearchUrl(artistName: string): string {
  return `https://www.kkbox.com/tw/tc/search?q=${encodeURIComponent(artistName)}`;
}

/**
 * 生成音乐平台链接
 */
export function generateMusicPlatformUrls(artistName: string) {
  return {
    qq_music_url: generateQQMusicSearchUrl(artistName),
    netease_url: generateNeteaseSearchUrl(artistName),
    apple_music_url: generateAppleMusicSearchUrl(artistName),
    youtube_music_url: generateYouTubeMusicSearchUrl(artistName),
    kkbox_url: generateKKBOXSearchUrl(artistName)
  };
}

/**
 * 检查URL是否是直接链接（而不是搜索链接）
 */
export function isDirectUrl(url: string): boolean {
  return !url.includes('/search');
}

/**
 * 获取URL的显示文本
 */
export function getUrlDisplayText(url: string, platform: 'qq_music' | 'netease' | 'apple_music' | 'youtube_music' | 'kkbox'): string {
  const isSearch = !isDirectUrl(url);
  
  switch (platform) {
    case 'qq_music':
      return isSearch ? '在QQ音乐中搜索' : '在QQ音乐中打开';
    case 'netease':
      return isSearch ? '在网易云音乐中搜索' : '在网易云音乐中打开';
    case 'apple_music':
      return isSearch ? '在Apple Music中搜索' : '在Apple Music中打开';
    case 'youtube_music':
      return isSearch ? '在YouTube Music中搜索' : '在YouTube Music中打开';
    case 'kkbox':
      return isSearch ? '在KKBOX中搜索' : '在KKBOX中打开';
    default:
      return '打开';
  }
}
