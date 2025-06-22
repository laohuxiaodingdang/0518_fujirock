import asyncio
import logging
import sys
from pathlib import Path
from typing import List, Dict, Any, Tuple

# Add project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from services.database_service import db_service

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ArtistDeduplicator:
    """清理数据库中重复的艺术家条目"""

    def __init__(self):
        self.db = db_service

    async def find_duplicates(self) -> List[Tuple[str, List[Dict[str, Any]]]]:
        """
        查找具有相同 Spotify ID 的重复艺术家。
        返回一个列表，每个元素是一个元组 (spotify_id, artists_list)
        """
        if not self.db.is_connected():
            logging.error("Database not connected.")
            return []

        logging.info("Finding duplicate artists by Spotify ID...")
        try:
            # 使用 PostgREST RPC 调用来执行复杂的聚合查询
            # 这个查询会按 spotify_id 分组，并找出所有 count > 1 的组
            response = self.db.supabase.rpc(
                'get_duplicate_artists_by_spotify_id'
            ).execute()
            
            if response.data:
                # PostgREST a GREST-en oinarritutako funtzioaren emaitza prozesatzen
                # The result is a list of objects, each with spotify_id and a list of artists
                duplicates = []
                for row in response.data:
                    spotify_id = row['spotify_id']
                    artists = row['artists']
                    if spotify_id and len(artists) > 1:
                        duplicates.append((spotify_id, artists))
                logging.info(f"Found {len(duplicates)} sets of duplicate artists.")
                return duplicates
            else:
                logging.info("No duplicate artists found.")
                return []
        except Exception as e:
            # Supabase Python库可能还不支持 group by + having, 我们需要手动处理
            logging.warning(f"RPC call failed, falling back to manual processing: {e}")
            return await self._find_duplicates_manual()

    async def _find_duplicates_manual(self) -> List[Tuple[str, List[Dict[str, Any]]]]:
        """手动查找重复项的后备方法"""
        logging.info("Manually finding duplicates...")
        response = self.db.supabase.table("artists").select("id, name, spotify_id").not_.is_("spotify_id", "null").execute()
        
        if not response.data:
            return []

        artists_by_spotify_id: Dict[str, List[Dict[str, Any]]] = {}
        for artist in response.data:
            sid = artist['spotify_id']
            if sid not in artists_by_spotify_id:
                artists_by_spotify_id[sid] = []
            artists_by_spotify_id[sid].append(artist)

        duplicates = []
        for spotify_id, artists in artists_by_spotify_id.items():
            if len(artists) > 1:
                logging.info(f"Found duplicates for Spotify ID {spotify_id}: {[a['name'] for a in artists]}")
                duplicates.append((spotify_id, artists))
        
        return duplicates

    def choose_primary_artist(self, artists: List[Dict[str, Any]]) -> Dict[str, Any]:
        """从重复列表中选择一个作为主条目"""
        # 策略：选择名字最长的那个，或者有大写字母的，通常是更完整的
        artists.sort(key=lambda x: len(x['name']), reverse=True)
        return artists[0]

    async def merge_performances(self, primary_artist_id: str, duplicate_ids: List[str]):
        """将重复条目的演出记录合并到主条目"""
        if not duplicate_ids:
            return

        logging.info(f"Merging performances from {duplicate_ids} to {primary_artist_id}...")
        try:
            result = self.db.supabase.table("performances").update(
                {"artist_id": primary_artist_id}
            ).in_("artist_id", duplicate_ids).execute()
            
            logging.info(f"Updated {len(result.data)} performance records.")
        except Exception as e:
            logging.error(f"Failed to merge performances: {e}")

    async def delete_duplicates(self, duplicate_ids: List[str]):
        """删除重复的艺术家条目"""
        if not duplicate_ids:
            return
            
        logging.info(f"Deleting duplicate artist records: {duplicate_ids}...")
        try:
            result = self.db.supabase.table("artists").delete().in_("id", duplicate_ids).execute()
            logging.info(f"Deleted {len(result.data)} duplicate artists.")
        except Exception as e:
            logging.error(f"Failed to delete duplicates: {e}")

    async def run(self):
        """执行去重流程"""
        logging.info("--- Starting Artist Deduplication Process ---")
        duplicate_sets = await self.find_duplicates()

        if not duplicate_sets:
            logging.info("No duplicates to process. Database is clean!")
            return

        for spotify_id, artists in duplicate_sets:
            logging.info(f"\nProcessing duplicates for Spotify ID: {spotify_id}")
            
            primary_artist = self.choose_primary_artist(artists)
            duplicate_artists = [a for a in artists if a['id'] != primary_artist['id']]
            duplicate_ids = [a['id'] for a in duplicate_artists]
            
            logging.info(f"  Primary artist: '{primary_artist['name']}' (ID: {primary_artist['id']})")
            logging.info(f"  Duplicate artists: {[a['name'] for a in duplicate_artists]}")

            # 1. 合并演出记录
            await self.merge_performances(primary_artist['id'], duplicate_ids)
            
            # 2. 删除重复艺术家
            await self.delete_duplicates(duplicate_ids)

        logging.info("\n--- Artist Deduplication Process Complete ---")


async def main():
    deduplicator = ArtistDeduplicator()
    await deduplicator.run()

if __name__ == "__main__":
    # 在 Supabase UI 的 SQL Editor 中运行以下代码来创建函数:
    # CREATE OR REPLACE FUNCTION get_duplicate_artists_by_spotify_id()
    # RETURNS TABLE(spotify_id TEXT, artists JSONB) AS $$
    # BEGIN
    #     RETURN QUERY
    #     SELECT
    #         a.spotify_id,
    #         jsonb_agg(jsonb_build_object('id', a.id, 'name', a.name)) AS artists
    #     FROM
    #         artists a
    #     WHERE
    #         a.spotify_id IS NOT NULL
    #     GROUP BY
    #         a.spotify_id
    #     HAVING
    #         count(a.id) > 1;
    # END;
    # $$ LANGUAGE plpgsql;
    asyncio.run(main()) 