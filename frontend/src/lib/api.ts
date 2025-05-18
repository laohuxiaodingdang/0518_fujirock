// API服务封装

/**
 * 搜索艺术家
 */
export async function searchArtists(query: string) {
  try {
    const response = await fetch(`/api/spotify/search?q=${encodeURIComponent(query)}`);
    if (!response.ok) throw new Error('搜索失败');
    return await response.json();
  } catch (error) {
    console.error('搜索艺术家失败:', error);
    throw error;
  }
}

/**
 * 获取艺术家详情
 */
export async function getArtistDetails(id: string) {
  try {
    const response = await fetch(`/api/spotify/artist/${id}`);
    if (!response.ok) throw new Error('获取艺术家详情失败');
    return await response.json();
  } catch (error) {
    console.error('获取艺术家详情失败:', error);
    throw error;
  }
}

/**
 * 获取艺术家维基百科信息
 */
export async function getArtistWikipedia(name: string) {
  try {
    const response = await fetch(`/api/wikipedia?name=${encodeURIComponent(name)}`);
    if (!response.ok) throw new Error('获取维基百科信息失败');
    return await response.json();
  } catch (error) {
    console.error('获取维基百科信息失败:', error);
    throw error;
  }
}

/**
 * 获取艺术家赛博朋克风格描述
 */
export async function getArtistDescription(name: string, genre?: string) {
  try {
    let url = `/api/description?name=${encodeURIComponent(name)}`;
    if (genre) url += `&genre=${encodeURIComponent(genre)}`;
    
    const response = await fetch(url);
    if (!response.ok) throw new Error('获取艺术家描述失败');
    return await response.json();
  } catch (error) {
    console.error('获取艺术家描述失败:', error);
    throw error;
  }
} 