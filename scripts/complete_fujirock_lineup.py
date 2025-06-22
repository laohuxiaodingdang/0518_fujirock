import asyncio
import logging
import sys
import re
from pathlib import Path
from typing import List, Dict, Any, Set
from datetime import datetime, timezone

# Add project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from services.artist_db_service import artist_db_service
from services.database_service import db_service

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FujiRockLineupCompleter:
    """补全 Fuji Rock 阵容到数据库"""
    
    def __init__(self):
        self.artist_db_service = artist_db_service
        self.lineup_file = "fujirock_lineup_from_image.txt"
        
    def parse_lineup_file(self) -> Dict[str, List[str]]:
        """解析阵容文件，提取所有艺术家和舞台信息"""
        logging.info(f"Parsing lineup file: {self.lineup_file}")
        
        artists_by_stage = {}
        current_stage = None
        
        try:
            with open(self.lineup_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith('===') or line.startswith('Fuji Rock'):
                    continue
                
                # 检查是否是舞台标题
                if line.startswith('### ') or line.startswith('## '):
                    current_stage = line.replace('#', '').strip()
                    artists_by_stage[current_stage] = []
                    continue
                
                # 检查是否是艺术家条目
                if line.startswith('- ') and current_stage:
                    artist_name = line[2:].strip()  # 移除 "- " 前缀
                    if artist_name:
                        artists_by_stage[current_stage].append(artist_name)
            
            logging.info(f"Parsed {len(artists_by_stage)} stages with artists")
            return artists_by_stage
            
        except FileNotFoundError:
            logging.error(f"Lineup file not found: {self.lineup_file}")
            return {}
        except Exception as e:
            logging.error(f"Error parsing lineup file: {str(e)}")
            return {}
    
    def get_all_artists_from_lineup(self) -> Set[str]:
        """从阵容文件中获取所有艺术家名字"""
        artists_by_stage = self.parse_lineup_file()
        all_artists = set()
        
        for stage, artists in artists_by_stage.items():
            for artist in artists:
                all_artists.add(artist)
        
        return all_artists
    
    async def get_existing_artists(self) -> Set[str]:
        """获取数据库中已存在的艺术家名字"""
        logging.info("Fetching existing artists from database...")
        
        try:
            response = db_service.supabase.table("artists").select("name").execute()
            existing_names = {artist["name"] for artist in response.data}
            logging.info(f"Found {len(existing_names)} existing artists in database")
            return existing_names
        except Exception as e:
            logging.error(f"Error fetching existing artists: {str(e)}")
            return set()
    
    async def add_missing_artists(self, missing_artists: List[str]) -> int:
        """添加缺失的艺术家到数据库"""
        if not missing_artists:
            logging.info("No missing artists to add")
            return 0
        
        added_count = 0
        total = len(missing_artists)
        
        logging.info(f"Adding {total} missing artists to database...")
        
        for i, artist_name in enumerate(missing_artists, 1):
            try:
                logging.info(f"[{i}/{total}] Adding: {artist_name}")
                
                # 准备艺术家数据
                artist_data = {
                    "name": artist_name,
                    "description": "",
                    "image_url": None,
                    "genres": [],
                    "is_fuji_rock_artist": True,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
                
                # 创建艺术家
                result = await self.artist_db_service.create_artist(artist_data)
                
                if result.get("success"):
                    logging.info(f"  ✅ Successfully added: {artist_name}")
                    added_count += 1
                else:
                    if "already exists" in result.get("error", ""):
                        logging.info(f"  ⚠️ Already exists: {artist_name}")
                    else:
                        logging.error(f"  ❌ Failed to add {artist_name}: {result.get('error')}")
                
                await asyncio.sleep(0.1)  # 避免API限流
                
            except Exception as e:
                logging.error(f"  ❌ Error adding {artist_name}: {str(e)}")
        
        return added_count
    
    async def complete_lineup(self):
        """补全阵容到数据库"""
        logging.info("=== Starting Fuji Rock Lineup Completion ===")
        
        # 1. 解析阵容文件
        lineup_artists = self.get_all_artists_from_lineup()
        logging.info(f"Total artists in lineup file: {len(lineup_artists)}")
        
        # 2. 获取已存在的艺术家
        existing_artists = await self.get_existing_artists()
        
        # 3. 找出缺失的艺术家
        missing_artists = list(lineup_artists - existing_artists)
        missing_artists.sort()  # 按字母顺序排序
        
        logging.info(f"Missing artists: {len(missing_artists)}")
        
        if missing_artists:
            logging.info("Missing artists list:")
            for i, artist in enumerate(missing_artists, 1):
                logging.info(f"  {i:3d}. {artist}")
        
        # 4. 添加缺失的艺术家
        added_count = await self.add_missing_artists(missing_artists)
        
        # 5. 最终统计
        logging.info("\n" + "="*60)
        logging.info("=== Fuji Rock Lineup Completion Summary ===")
        logging.info(f"  Total artists in lineup: {len(lineup_artists)}")
        logging.info(f"  Existing in database: {len(existing_artists)}")
        logging.info(f"  Missing artists: {len(missing_artists)}")
        logging.info(f"  Successfully added: {added_count}")
        logging.info(f"  Failed to add: {len(missing_artists) - added_count}")
        logging.info("="*60)

async def main():
    completer = FujiRockLineupCompleter()
    await completer.complete_lineup()

if __name__ == "__main__":
    asyncio.run(main()) 