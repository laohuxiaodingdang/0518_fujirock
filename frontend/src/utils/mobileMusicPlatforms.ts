/**
 * 移动端音乐平台跳转工具
 * 提供多种实用的跳转策略
 */

// 检测是否为移动端
export function isMobile(): boolean {
  return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
}

// 检测是否为微信浏览器
export function isWeChat(): boolean {
  return /MicroMessenger/i.test(navigator.userAgent);
}

// 检测是否为iOS
export function isIOS(): boolean {
  return /iPad|iPhone|iPod/.test(navigator.userAgent);
}

// 检测是否为Android
export function isAndroid(): boolean {
  return /Android/.test(navigator.userAgent);
}

/**
 * QQ音乐实用跳转
 * 策略：提供多种选择给用户
 */
export function openQQMusic(artistName: string): void {
  const encodedName = encodeURIComponent(artistName);
  
  if (isMobile()) {
    // 移动端：提供选择
    const choice = confirm(
      `QQ音乐跳转选项：\n\n` +
      `• 确定：尝试打开QQ音乐App\n` +
      `• 取消：打开应用商店下载App\n\n` +
      `搜索关键词：${artistName}`
    );
    
    if (choice) {
      // 尝试打开App
      window.location.href = 'qqmusic://';
      
      // 3秒后如果还在当前页面，提示用户
      setTimeout(() => {
        if (!document.hidden) {
          alert('QQ音乐App可能未安装，请从应用商店下载');
        }
      }, 3000);
    } else {
      // 打开应用商店
      if (isIOS()) {
        window.open('https://apps.apple.com/cn/app/qq音乐/id414603431', '_blank');
      } else if (isAndroid()) {
        window.open('https://play.google.com/store/apps/details?id=com.tencent.qqmusic', '_blank');
      } else {
        window.open('https://y.qq.com/download/', '_blank');
      }
    }
  } else {
    // 桌面端：直接跳转网页版
    window.open(`https://y.qq.com/n/ryqq/search?w=${encodedName}`, '_blank');
  }
}

/**
 * 网易云音乐实用跳转
 * 策略：提供多种选择给用户
 */
export function openNeteaseMusic(artistName: string): void {
  const encodedName = encodeURIComponent(artistName);
  
  if (isMobile()) {
    // 移动端：提供选择
    const choice = confirm(
      `网易云音乐跳转选项：\n\n` +
      `• 确定：尝试打开网易云音乐App\n` +
      `• 取消：打开应用商店下载App\n\n` +
      `搜索关键词：${artistName}`
    );
    
    if (choice) {
      // 尝试打开App
      window.location.href = 'orpheus://';
      
      // 3秒后如果还在当前页面，提示用户
      setTimeout(() => {
        if (!document.hidden) {
          alert('网易云音乐App可能未安装，请从应用商店下载');
        }
      }, 3000);
    } else {
      // 打开应用商店
      if (isIOS()) {
        window.open('https://apps.apple.com/cn/app/网易云音乐/id590338362', '_blank');
      } else if (isAndroid()) {
        window.open('https://play.google.com/store/apps/details?id=com.netease.cloudmusic', '_blank');
      } else {
        window.open('https://music.163.com/#/download', '_blank');
      }
    }
  } else {
    // 桌面端：直接跳转网页版
    window.open(`https://music.163.com/#/search/m/?s=${encodedName}&type=100`, '_blank');
  }
}

/**
 * 获取平台提示文本
 */
export function getPlatformTipText(platform: 'qq' | 'netease'): string {
  if (!isMobile()) {
    return `在${platform === 'qq' ? 'QQ音乐' : '网易云音乐'}中搜索`;
  }
  
  if (isWeChat()) {
    return `点击后请选择"在浏览器中打开"以使用App`;
  }
  
  return `点击打开${platform === 'qq' ? 'QQ音乐' : '网易云音乐'}App`;
}

/**
 * 更友好的跳转方式 - 带搜索提示
 */
export function openMusicPlatformWithSearchHint(platform: 'qq' | 'netease', artistName: string): void {
  const platformName = platform === 'qq' ? 'QQ音乐' : '网易云音乐';
  
  if (isMobile()) {
    const choice = confirm(
      `${platformName}跳转：\n\n` +
      `• 确定：打开${platformName}App\n` +
      `• 取消：打开应用商店\n\n` +
      `提示：App打开后请手动搜索"${artistName}"`
    );
    
    if (choice) {
      // 打开App
      if (platform === 'qq') {
        window.location.href = 'qqmusic://';
      } else {
        window.location.href = 'orpheus://';
      }
      
      // 2秒后显示搜索提示
      setTimeout(() => {
        alert(`请在${platformName}App中搜索：${artistName}`);
      }, 2000);
    } else {
      // 打开应用商店
      if (platform === 'qq') {
        if (isIOS()) {
          window.open('https://apps.apple.com/cn/app/qq音乐/id414603431', '_blank');
        } else {
          window.open('https://play.google.com/store/apps/details?id=com.tencent.qqmusic', '_blank');
        }
      } else {
        if (isIOS()) {
          window.open('https://apps.apple.com/cn/app/网易云音乐/id590338362', '_blank');
        } else {
          window.open('https://play.google.com/store/apps/details?id=com.netease.cloudmusic', '_blank');
        }
      }
    }
  } else {
    // 桌面端：直接跳转网页版
    const encodedName = encodeURIComponent(artistName);
    if (platform === 'qq') {
      window.open(`https://y.qq.com/n/ryqq/search?w=${encodedName}`, '_blank');
    } else {
      window.open(`https://music.163.com/#/search/m/?s=${encodedName}&type=100`, '_blank');
    }
  }
}
