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

class WikiCoverageAnalyzer:
    """
    分析数据库中 artists 表的 wiki_data 和 wiki_extract 字段的覆盖情况。
    """
    def __init__(self):
        self.db_service = artist_db_service

    async def run(self):
        """执行分析流程"""
        logging.info("--- Analyzing Wiki Data Coverage ---")

        # 1. 获取所有艺术家的相关数据
        logging.info("Fetching all artists from the database...")
        response = self.db_service.db.supabase.table("artists").select("name, wiki_data, wiki_extract, spotify_id").execute()

        if not response.data:
            logging.error("Could not fetch any artists from the database. Aborting.")
            return

        artists = response.data
        total_artists = len(artists)
        
        # 2. 分析 wiki_data 字段
        artists_with_wiki_data = []
        artists_without_wiki_data = []
        
        for artist in artists:
            if artist.get('wiki_data'):
                artists_with_wiki_data.append(artist)
            else:
                artists_without_wiki_data.append(artist)
        
        wiki_data_coverage = (len(artists_with_wiki_data) / total_artists) * 100 if total_artists > 0 else 0
        
        # 3. 分析 wiki_extract 字段
        artists_with_wiki_extract = []
        artists_without_wiki_extract = []
        
        for artist in artists:
            if artist.get('wiki_extract'):
                artists_with_wiki_extract.append(artist)
            else:
                artists_without_wiki_extract.append(artist)
        
        wiki_extract_coverage = (len(artists_with_wiki_extract) / total_artists) * 100 if total_artists > 0 else 0
        
        # 4. 统计和报告
        logging.info("\n--- Wiki Coverage Report ---")
        
        print(f"\n📊 Total Artists: {total_artists}")
        print(f"\n📚 Wiki Data Field:")
        print(f"  ✅ Artists with Wiki Data: {len(artists_with_wiki_data)}")
        print(f"  ❌ Artists without Wiki Data: {len(artists_without_wiki_data)}")
        print(f"  📊 Wiki Data Coverage: {wiki_data_coverage:.2f}%")
        
        print(f"\n📖 Wiki Extract Field:")
        print(f"  ✅ Artists with Wiki Extract: {len(artists_with_wiki_extract)}")
        print(f"  ❌ Artists without Wiki Extract: {len(artists_without_wiki_extract)}")
        print(f"  📊 Wiki Extract Coverage: {wiki_extract_coverage:.2f}%")
        
        # 5. 抽样检查
        if artists_with_wiki_data:
            logging.info("\n--- Sample Wiki Data ---")
            
            # 抽取最多 3 个样本
            sample_size = min(3, len(artists_with_wiki_data))
            samples = random.sample(artists_with_wiki_data, sample_size)
            
            for i, sample in enumerate(samples, 1):
                print(f"\n--- Sample {i} ---")
                print(f"  Artist Name: {sample['name']}")
                wiki_data = sample['wiki_data']
                if isinstance(wiki_data, dict):
                    print(f"  Wiki Data Keys: {list(wiki_data.keys())}")
                    if 'extract' in wiki_data:
                        print(f"  Extract Preview: \"{wiki_data['extract'][:100]}...\"")
                else:
                    print(f"  Wiki Data Type: {type(wiki_data)}")
                    print(f"  Wiki Data Preview: \"{str(wiki_data)[:100]}...\"")

        if artists_with_wiki_extract:
            logging.info("\n--- Sample Wiki Extracts ---")
            
            # 抽取最多 3 个样本
            sample_size = min(3, len(artists_with_wiki_extract))
            samples = random.sample(artists_with_wiki_extract, sample_size)
            
            for i, sample in enumerate(samples, 1):
                print(f"\n--- Sample {i} ---")
                print(f"  Artist Name: {sample['name']}")
                wiki_extract = sample['wiki_extract']
                print(f"  Wiki Extract Preview: \"{wiki_extract[:100]}...\"")

        # 6. 分析缺失数据的艺术家
        if artists_without_wiki_data:
            logging.info("\n--- Analysis of Artists Missing Wiki Data ---")
            
            missing_with_spotify = 0
            missing_without_spotify = 0
            
            print("\nList of artists missing wiki_data:")
            for artist in artists_without_wiki_data:
                name = artist['name']
                has_spotify = "✅" if artist.get('spotify_id') else "❌"
                print(f"  - {name} (Has Spotify ID: {has_spotify})")

                if artist.get('spotify_id'):
                    missing_with_spotify += 1
                else:
                    missing_without_spotify += 1

            print(f"\nSummary of missing wiki_data:")
            print(f"  - Could potentially be filled by Wiki search: {missing_with_spotify}")
            print(f"  - No Spotify ID (harder to find): {missing_without_spotify}")

        logging.info("\n--- Analysis Complete ---")


async def main():
    analyzer = WikiCoverageAnalyzer()
    await analyzer.run()

if __name__ == "__main__":
    asyncio.run(main()) 