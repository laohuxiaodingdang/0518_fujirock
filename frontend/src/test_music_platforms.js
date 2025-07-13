// 测试音乐平台服务
const { generateMusicPlatformUrls, getUrlDisplayText } = require('./services/music_platforms');

console.log('=== 测试音乐平台服务 ===');

// 测试生成链接
const testArtist = 'Vampire Weekend';
const urls = generateMusicPlatformUrls(testArtist);

console.log(`艺术家: ${testArtist}`);
console.log(`QQ音乐链接: ${urls.qq_music_url}`);
console.log(`网易云音乐链接: ${urls.netease_url}`);

// 测试显示文本
console.log(`QQ音乐显示文本: ${getUrlDisplayText(urls.qq_music_url, 'qq_music')}`);
console.log(`网易云音乐显示文本: ${getUrlDisplayText(urls.netease_url, 'netease')}`);

// 测试直接链接
const directQQUrl = 'https://y.qq.com/n/ryqq/singer/003LaMHm42u7qH';
const directNeteaseUrl = 'https://music.163.com/#/artist?id=98351';

console.log(`直接QQ音乐链接显示文本: ${getUrlDisplayText(directQQUrl, 'qq_music')}`);
console.log(`直接网易云音乐链接显示文本: ${getUrlDisplayText(directNeteaseUrl, 'netease')}`);
