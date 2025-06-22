import asyncio
import logging
import sys
import random
from pathlib import Path
from typing import List, Dict, Any

# Add project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from services.artist_db_service import artist_db_service

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DescriptionAnalyzer:
    """
    分析数据库中 artists 表的 description 字段的覆盖情况和内容。
    """
    def __init__(self):
        self.db_service = artist_db_service

    async def run(self):
        """执行分析流程"""
        logging.info("--- Analyzing Description Field Coverage ---")

        # 1. 获取所有艺术家的相关数据
        logging.info("Fetching all artists from the database...")
        response = self.db_service.db.supabase.table("artists").select("name, description, wiki_extract, spotify_id").execute()

        if not response.data:
            logging.error("Could not fetch any artists from the database. Aborting.")
            return

        artists = response.data
        total_artists = len(artists)
        
        artists_with_desc = []
        artists_without_desc = []

        for artist in artists:
            if artist.get('description'):
                artists_with_desc.append(artist)
            else:
                artists_without_desc.append(artist)
        
        # 2. 统计和报告
        logging.info("\n--- Coverage Report ---")
        desc_coverage = (len(artists_with_desc) / total_artists) * 100 if total_artists > 0 else 0
        
        print(f"\n✅ Total Artists: {total_artists}")
        print(f"✅ Artists with Description: {len(artists_with_desc)}")
        print(f"❌ Artists without Description: {len(artists_without_desc)}")
        print(f"📊 Description Field Coverage: {desc_coverage:.2f}%")
        
        # 3. 抽样检查
        if artists_with_desc:
            logging.info("\n--- Sample Descriptions ---")
            
            # 抽取最多 5 个样本
            sample_size = min(5, len(artists_with_desc))
            samples = random.sample(artists_with_desc, sample_size)
            
            for i, sample in enumerate(samples, 1):
                print(f"\n--- Sample {i} ---")
                print(f"  Artist Name: {sample['name']}")
                
                # 判断描述的可能来源
                description = sample['description']
                source = "Unknown"
                if description.strip().startswith("Genres:"):
                    source = "Spotify Genres"
                elif sample.get('wiki_extract') and sample['wiki_extract'].strip() in description:
                     source = "Wikipedia Extract"
                elif len(description) > 50:
                     source = "Likely Wikipedia Extract"

                print(f"  Description: \"{description}\"")
                print(f"  Possible Source: {source}")

        # 4. 分析缺失描述的艺术家
        if artists_without_desc:
            logging.info("\n--- Analysis of Artists Missing Description ---")
            
            missing_with_spotify = 0
            missing_with_wiki = 0
            missing_with_nothing = 0
            
            print("\nList of artists missing descriptions:")
            for artist in artists_without_desc:
                name = artist['name']
                has_spotify = "✅" if artist.get('spotify_id') else "❌"
                has_wiki = "✅" if artist.get('wiki_extract') else "❌"
                print(f"  - {name} (Has Spotify ID: {has_spotify}, Has Wiki: {has_wiki})")

                if artist.get('spotify_id'):
                    missing_with_spotify += 1
                if artist.get('wiki_extract'):
                    missing_with_wiki += 1
                if not artist.get('spotify_id') and not artist.get('wiki_extract'):
                    missing_with_nothing += 1

            print(f"\nSummary of missing descriptions:")
            print(f"  - Could potentially be filled by Spotify: {missing_with_spotify}")
            print(f"  - Could potentially be filled by Wiki: {missing_with_wiki}")
            print(f"  - No immediate data source (Spotify/Wiki): {missing_with_nothing}")

        logging.info("\n--- Analysis Complete ---")


async def main():
    analyzer = DescriptionAnalyzer()
    await analyzer.run()

if __name__ == "__main__":
    asyncio.run(main()) 