// API 基础配置 - 直接连接后端服务器
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// API 响应类型定义
export interface WikipediaArtistResponse {
  success: boolean;
  data: {
    title: string;
    extract: string;
    thumbnail?: {
      source: string;
      width: number;
      height: number;
    };
    categories: string[];
    references: Array<{
      title: string;
      url: string;
    }>;
  };
}

// Spotify API 响应类型
export interface SpotifyArtistResponse {
  success: boolean;
  data: {
    id: string;
    name: string;
    popularity: number;
    followers: {
      total: number;
    };
    genres: string[];
    images: Array<{
      url: string;
      height: number;
      width: number;
    }>;
    external_urls: {
      spotify: string;
    };
  };
}

// Spotify 热门歌曲响应类型
export interface SpotifyTopTracksResponse {
  success: boolean;
  data: {
    tracks: Array<{
      id: string;
      name: string;
      duration_ms: number;
      preview_url: string | null;
      album: {
        name: string;
        images: Array<{
          url: string;
          height: number;
          width: number;
        }>;
      };
      external_urls: {
        spotify: string;
      };
    }>;
  };
}

// AI 描述生成响应类型
export interface AIDescriptionResponse {
  success: boolean;
  data: {
    original_content: string;
    sassy_description: string;
    style_metrics: {
      humor_level: number;
      sarcasm_level: number;
      fact_accuracy: number;
    };
    generated_at: string;
    model_used: string;
    tokens_used: number;
  };
}

// 错误响应类型
export interface ApiError {
  success: false;
  error: string;
  message: string;
}

// 通用API请求函数
const apiRequest = async <T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> => {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const defaultOptions: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(url, defaultOptions);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
};

// 获取艺术家Wikipedia信息
export const getArtistWikipedia = async (
  artistName: string,
  language: string = "zh"
): Promise<WikipediaArtistResponse> => {
  if (!artistName.trim()) {
    throw new Error('Artist name is required');
  }

  const encodedArtistName = encodeURIComponent(artistName.trim());
  return apiRequest<WikipediaArtistResponse>(
    `/api/wikipedia/artists/${encodedArtistName}?language=${language}`
  );
};

// 获取艺术家Spotify信息
export const getArtistSpotify = async (
  artistName: string
): Promise<SpotifyArtistResponse> => {
  if (!artistName.trim()) {
    throw new Error('Artist name is required');
  }

  const encodedArtistName = encodeURIComponent(artistName.trim());
  return apiRequest<SpotifyArtistResponse>(
    `/api/spotify/artist-by-name/${encodedArtistName}`
  );
};

// 获取艺术家热门歌曲
export const getArtistTopTracks = async (
  artistName: string
): Promise<SpotifyTopTracksResponse> => {
  if (!artistName.trim()) {
    throw new Error('Artist name is required');
  }

  const encodedArtistName = encodeURIComponent(artistName.trim());
  return apiRequest<SpotifyTopTracksResponse>(
    `/api/spotify/artist-by-name/${encodedArtistName}/top-tracks`
  );
};

// 生成AI毒舌描述
export const generateArtistDescription = async (
  artistName: string,
  wikiContent: string,
  intensity: number = 5
): Promise<AIDescriptionResponse> => {
  if (!artistName.trim()) {
    throw new Error('Artist name is required');
  }

  return apiRequest<AIDescriptionResponse>('/api/ai/generate-description', {
    method: 'POST',
    body: JSON.stringify({
      artist_name: artistName,
      wiki_content: wikiContent,
      style_intensity: intensity,
      language: 'zh',
      max_length: 500,
      temperature: 0.7,
    }),
  });
};

// 生成AI毒舌描述 - 流式版本
export const generateArtistDescriptionStream = async (
  artistName: string,
  wikiContent: string,
  intensity: number = 5,
  onUpdate: (content: string) => void,
  onComplete: (data: any) => void,
  onError: (error: string) => void
): Promise<void> => {
  if (!artistName.trim()) {
    throw new Error('Artist name is required');
  }

  const requestData = {
    artist_name: artistName,
    wiki_content: wikiContent,
    style_intensity: intensity,
    language: 'zh',
    max_length: 500,
    temperature: 0.7,
  };

  try {
    const response = await fetch('/api/ai/generate-description-stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestData),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('Response body is not readable');
    }

    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      
      // 处理 SSE 数据
      const lines = buffer.split('\n');
      buffer = lines.pop() || ''; // 保留不完整的行

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6));
            
            if (data.type === 'content') {
              onUpdate(data.content);
            } else if (data.type === 'complete') {
              onComplete(data);
              return;
            } else if (data.type === 'error') {
              onError(data.error);
              return;
            }
          } catch (e) {
            console.error('Failed to parse SSE data:', e);
          }
        }
      }
    }
  } catch (error) {
    console.error('Stream request failed:', error);
    onError(error instanceof Error ? error.message : 'Unknown error');
  }
};

// 获取艺术家完整信息（组合多个API）
export const getArtistFullProfile = async (artistName: string) => {
  try {
    // 并行调用多个API
    const [wikipediaData, spotifyData, topTracksData] = await Promise.allSettled([
      getArtistWikipedia(artistName),
      getArtistSpotify(artistName),
      getArtistTopTracks(artistName),
    ]);

    // 处理Wikipedia数据
    const wikipedia = wikipediaData.status === 'fulfilled' ? wikipediaData.value : null;
    
    // 处理Spotify数据
    const spotify = spotifyData.status === 'fulfilled' ? spotifyData.value : null;
    
    // 处理热门歌曲数据
    const topTracks = topTracksData.status === 'fulfilled' ? topTracksData.value : null;

    // 如果有Wikipedia内容，生成AI描述
    let aiDescription = null;
    if (wikipedia?.success && wikipedia.data.extract) {
      try {
        aiDescription = await generateArtistDescription(
          artistName,
          wikipedia.data.extract,
          7 // 默认毒舌程度为7
        );
      } catch (error) {
        console.error('Failed to generate AI description:', error);
      }
    }

    return {
      wikipedia,
      spotify,
      topTracks,
      aiDescription,
      errors: {
        wikipedia: wikipediaData.status === 'rejected' ? wikipediaData.reason : null,
        spotify: spotifyData.status === 'rejected' ? spotifyData.reason : null,
        topTracks: topTracksData.status === 'rejected' ? topTracksData.reason : null,
      }
    };
  } catch (error) {
    console.error('Failed to get artist full profile:', error);
    throw error;
  }
}; 