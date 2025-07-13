export interface Artist {
  id: string;
  name: string;
  description?: string;
  image_url?: string;
  wiki_data?: any;
  wiki_extract?: string;
  spotify_id?: string;
  spotify_url?: string;
  qq_music_url?: string;
  netease_url?: string;
  genres?: string[];
  is_fuji_rock_artist: boolean;
  created_at: string;
  updated_at: string;
}

export interface ArtistMusicPlatforms {
  spotify?: {
    url: string;
    preview_url?: string;
  };
  qq_music?: {
    url: string;
  };
  netease?: {
    url: string;
    preview_url?: string;
  };
}
