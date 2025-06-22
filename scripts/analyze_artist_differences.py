import asyncio
import logging
import sys
from pathlib import Path
from typing import Set, List

# Add project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from services.database_service import db_service

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ArtistDifferenceAnalyzer:
    """分析阵容文件和数据库中的艺术家差异"""
    
    def __init__(self):
        self.lineup_file = "fujirock_lineup_from_image.txt"
        
    def parse_lineup_file(self) -> Set[str]:
        """解析阵容文件，提取所有艺术家名字"""
        logging.info(f"Parsing lineup file: {self.lineup_file}")
        
        artists = set()
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
                    continue
                
                # 检查是否是艺术家条目
                if line.startswith('- ') and current_stage:
                    artist_name = line[2:].strip()  # 移除 "- " 前缀
                    if artist_name:
                        artists.add(artist_name)
            
            logging.info(f"Found {len(artists)} artists in lineup file")
            return artists
            
        except FileNotFoundError:
            logging.error(f"Lineup file not found: {self.lineup_file}")
            return set()
        except Exception as e:
            logging.error(f"Error parsing lineup file: {str(e)}")
            return set()
    
    async def get_database_artists(self) -> Set[str]:
        """获取数据库中的所有艺术家名字"""
        logging.info("Fetching all artists from database...")
        
        try:
            response = db_service.supabase.table("artists").select("name, is_fuji_rock_artist").execute()
            
            all_artists = {artist["name"] for artist in response.data}
            fuji_rock_artists = {artist["name"] for artist in response.data if artist.get("is_fuji_rock_artist")}
            
            logging.info(f"Total artists in database: {len(all_artists)}")
            logging.info(f"Fuji Rock artists in database: {len(fuji_rock_artists)}")
            
            return all_artists, fuji_rock_artists
            
        except Exception as e:
            logging.error(f"Error fetching database artists: {str(e)}")
            return set(), set()
    
    def analyze_differences(self, lineup_artists: Set[str], db_artists: Set[str], fuji_rock_artists: Set[str]):
        """分析差异"""
        logging.info("\n" + "="*60)
        logging.info("=== Artist Difference Analysis ===")
        logging.info("="*60)
        
        # 1. 阵容文件中有但数据库中没有的
        missing_in_db = lineup_artists - db_artists
        logging.info(f"\n📋 Artists in lineup but missing in database ({len(missing_in_db)}):")
        if missing_in_db:
            for i, artist in enumerate(sorted(missing_in_db), 1):
                logging.info(f"  {i:2d}. {artist}")
        else:
            logging.info("  None")
        
        # 2. 数据库中有但阵容文件中没有的
        extra_in_db = db_artists - lineup_artists
        logging.info(f"\n➕ Artists in database but not in lineup ({len(extra_in_db)}):")
        if extra_in_db:
            for i, artist in enumerate(sorted(extra_in_db), 1):
                logging.info(f"  {i:2d}. {artist}")
        else:
            logging.info("  None")
        
        # 3. 数据库中的 Fuji Rock 艺术家
        logging.info(f"\n🎵 Fuji Rock artists in database ({len(fuji_rock_artists)}):")
        for i, artist in enumerate(sorted(fuji_rock_artists), 1):
            logging.info(f"  {i:2d}. {artist}")
        
        # 4. 统计信息
        logging.info(f"\n📊 Summary:")
        logging.info(f"  Lineup file artists: {len(lineup_artists)}")
        logging.info(f"  Total database artists: {len(db_artists)}")
        logging.info(f"  Fuji Rock artists in DB: {len(fuji_rock_artists)}")
        logging.info(f"  Missing in DB: {len(missing_in_db)}")
        logging.info(f"  Extra in DB: {len(extra_in_db)}")
        logging.info(f"  Common artists: {len(lineup_artists & db_artists)}")
        
        # 5. 检查是否有重复或相似的名字
        logging.info(f"\n🔍 Checking for similar names...")
        lineup_lower = {name.lower() for name in lineup_artists}
        db_lower = {name.lower() for name in db_artists}
        
        similar_names = lineup_lower & db_lower
        if similar_names:
            logging.info(f"Found {len(similar_names)} artists with similar names (case-insensitive):")
            for name in sorted(similar_names):
                logging.info(f"  - {name}")
    
    async def analyze(self):
        """执行完整分析"""
        logging.info("=== Starting Artist Difference Analysis ===")
        
        # 1. 解析阵容文件
        lineup_artists = self.parse_lineup_file()
        
        # 2. 获取数据库艺术家
        db_artists, fuji_rock_artists = await self.get_database_artists()
        
        # 3. 分析差异
        self.analyze_differences(lineup_artists, db_artists, fuji_rock_artists)

async def main():
    analyzer = ArtistDifferenceAnalyzer()
    await analyzer.analyze()

if __name__ == "__main__":
    asyncio.run(main()) 