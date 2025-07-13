// 简单收藏服务 - 使用本地存储，无需登录
export interface FavoriteArtist {
  id: string;
  name: string;
  image_url?: string;
  genres?: string[];
  created_at: string;
}

class SimpleFavoriteService {
  private readonly STORAGE_KEY = 'fuji_rock_favorites';

  // 获取所有收藏
  getFavorites(): FavoriteArtist[] {
    try {
      const stored = localStorage.getItem(this.STORAGE_KEY);
      return stored ? JSON.parse(stored) : [];
    } catch (error) {
      console.error('Error reading favorites from localStorage:', error);
      return [];
    }
  }

  // 保存收藏到本地
  saveFavorites(favorites: FavoriteArtist[]): void {
    try {
      localStorage.setItem(this.STORAGE_KEY, JSON.stringify(favorites));
    } catch (error) {
      console.error('Error saving favorites to localStorage:', error);
    }
  }

  // 检查是否已收藏
  isFavorited(artistId: string): boolean {
    const favorites = this.getFavorites();
    return favorites.some(fav => fav.id === artistId);
  }

  // 添加收藏
  addFavorite(artistId: string, artistName: string, imageUrl?: string, genres?: string[]): boolean {
    try {
      const favorites = this.getFavorites();
      
      // 检查是否已经收藏
      if (this.isFavorited(artistId)) {
        return false;
      }

      const newFavorite: FavoriteArtist = {
        id: artistId,
        name: artistName,
        image_url: imageUrl,
        genres: genres,
        created_at: new Date().toISOString()
      };

      favorites.push(newFavorite);
      this.saveFavorites(favorites);
      return true;
    } catch (error) {
      console.error('Error adding favorite:', error);
      return false;
    }
  }

  // 移除收藏
  removeFavorite(artistId: string): boolean {
    try {
      const favorites = this.getFavorites();
      const filtered = favorites.filter(fav => fav.id !== artistId);
      this.saveFavorites(filtered);
      return true;
    } catch (error) {
      console.error('Error removing favorite:', error);
      return false;
    }
  }

  // 切换收藏状态
  toggleFavorite(artistId: string, artistName: string, imageUrl?: string, genres?: string[]): boolean {
    if (this.isFavorited(artistId)) {
      return this.removeFavorite(artistId);
    } else {
      return this.addFavorite(artistId, artistName, imageUrl, genres);
    }
  }

  // 获取收藏数量
  getFavoriteCount(): number {
    return this.getFavorites().length;
  }

  // 清除所有收藏
  clearAllFavorites(): void {
    try {
      localStorage.removeItem(this.STORAGE_KEY);
    } catch (error) {
      console.error('Error clearing favorites:', error);
    }
  }
}

export const simpleFavoriteService = new SimpleFavoriteService();
