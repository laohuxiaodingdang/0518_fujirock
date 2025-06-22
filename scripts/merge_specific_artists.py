import asyncio
import logging
import sys
from pathlib import Path
from typing import List, Dict, Any, Union

# Add project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from services.database_service import db_service

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SpecificArtistMerger:
    """
    手动合并特定的重复艺术家条目。
    """
    def __init__(self):
        self.db = db_service
        # 定义主艺术家名称到其别名/重复项的映射
        self.merge_map: Dict[str, List[str]] = {
            "Fred again..": ["FRED AGAIN.."],
            "Night Tempo": ["NIGHT TEMPO"],
            "Suchmos": ["suchmos"], # 假定小写是重复项
            "T字路s": ["T字路s (T-jiros)", "T字路s (Tjiros)"]
        }

    async def get_artist_by_name(self, name: str) -> Union[Dict[str, Any], None]:
        """按名称获取单个艺术家"""
        try:
            response = self.db.supabase.table("artists").select("*").eq("name", name).limit(1).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            logging.error(f"Error fetching artist '{name}': {e}")
            return None

    async def merge_performances(self, primary_artist_id: str, duplicate_artist_id: str):
        """将单个重复艺术家的演出合并到主艺术家"""
        logging.info(f"Merging performances from {duplicate_artist_id} to {primary_artist_id}...")
        try:
            result = self.db.supabase.table("performances").update(
                {"artist_id": primary_artist_id}
            ).eq("artist_id", duplicate_artist_id).execute()
            logging.info(f"  - Updated {len(result.data)} performance records.")
        except Exception as e:
            logging.error(f"  - Failed to merge performances: {e}")

    async def delete_artist(self, artist_id: str):
        """删除单个艺术家"""
        logging.info(f"Deleting duplicate artist record: {artist_id}...")
        try:
            result = self.db.supabase.table("artists").delete().eq("id", artist_id).execute()
            logging.info(f"  - Deleted {len(result.data)} duplicate artist.")
        except Exception as e:
            logging.error(f"  - Failed to delete duplicate: {e}")

    async def run(self):
        """执行合并和删除流程"""
        logging.info("--- Starting Specific Artist Merge Process ---")
        if not self.db.is_connected():
            logging.error("Database not connected.")
            return

        for primary_name, alias_names in self.merge_map.items():
            logging.info(f"\nProcessing '{primary_name}' and its aliases {alias_names}...")
            
            primary_artist = await self.get_artist_by_name(primary_name)
            if not primary_artist:
                logging.warning(f"  - Primary artist '{primary_name}' not found. Skipping.")
                continue
            
            logging.info(f"  - Found primary artist '{primary_name}' (ID: {primary_artist['id']})")

            for alias_name in alias_names:
                alias_artist = await self.get_artist_by_name(alias_name)
                if not alias_artist:
                    logging.warning(f"  - Alias '{alias_name}' not found. Nothing to merge.")
                    continue
                
                logging.info(f"  - Found alias '{alias_name}' (ID: {alias_artist['id']}) to merge.")
                
                # 1. 合并演出记录
                await self.merge_performances(primary_artist['id'], alias_artist['id'])
                
                # 2. 删除重复艺术家
                await self.delete_artist(alias_artist['id'])

        logging.info("\n--- Specific Artist Merge Process Complete ---")

async def main():
    merger = SpecificArtistMerger()
    await merger.run()

if __name__ == "__main__":
    asyncio.run(main()) 