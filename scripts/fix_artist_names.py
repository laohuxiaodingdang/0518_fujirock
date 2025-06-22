import asyncio
import logging
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from services.database_service import db_service

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ArtistNameFixer:
    """修复艺术家名字差异和重复条目"""
    
    def __init__(self):
        self.db = db_service
    
    async def fix_egowrappin_name(self):
        """修复 EGO-WRAPPIN' 的名字"""
        logging.info("Fixing EGO-WRAPPIN' name...")
        
        try:
            # 查找 EGOWRAPPIN' 并更新为 EGO-WRAPPIN'
            result = self.db.supabase.table("artists").update({
                "name": "EGO-WRAPPIN'",
                "updated_at": "2025-06-21T21:15:00Z"
            }).eq("name", "EGOWRAPPIN'").execute()
            
            if result.data:
                logging.info("✅ Successfully updated EGOWRAPPIN' to EGO-WRAPPIN'")
            else:
                logging.info("⚠️ No EGOWRAPPIN' found to update")
                
        except Exception as e:
            logging.error(f"❌ Error updating EGOWRAPPIN': {str(e)}")
    
    async def remove_duplicates(self):
        """移除重复的艺术家条目"""
        logging.info("Checking for duplicate artists...")
        
        try:
            # 获取所有艺术家名字
            response = self.db.supabase.table("artists").select("id, name").execute()
            artists = response.data
            
            # 按名字分组
            name_groups = {}
            for artist in artists:
                name = artist["name"]
                if name not in name_groups:
                    name_groups[name] = []
                name_groups[name].append(artist["id"])
            
            # 找出重复的名字
            duplicates = {name: ids for name, ids in name_groups.items() if len(ids) > 1}
            
            if duplicates:
                logging.info(f"Found {len(duplicates)} duplicate names:")
                for name, ids in duplicates.items():
                    logging.info(f"  {name}: {len(ids)} entries")
                
                # 删除重复条目（保留第一个）
                for name, ids in duplicates.items():
                    # 保留第一个，删除其余的
                    ids_to_delete = ids[1:]
                    for artist_id in ids_to_delete:
                        try:
                            delete_result = self.db.supabase.table("artists").delete().eq("id", artist_id).execute()
                            if delete_result.data:
                                logging.info(f"  ✅ Deleted duplicate: {name} (ID: {artist_id})")
                            else:
                                logging.info(f"  ⚠️ Failed to delete: {name} (ID: {artist_id})")
                        except Exception as e:
                            logging.error(f"  ❌ Error deleting {name} (ID: {artist_id}): {str(e)}")
            else:
                logging.info("✅ No duplicates found")
                
        except Exception as e:
            logging.error(f"❌ Error checking duplicates: {str(e)}")
    
    async def verify_fixes(self):
        """验证修复结果"""
        logging.info("Verifying fixes...")
        
        try:
            # 检查 EGO-WRAPPIN' 是否存在
            egowrappin_result = self.db.supabase.table("artists").select("name").eq("name", "EGO-WRAPPIN'").execute()
            if egowrappin_result.data:
                logging.info("✅ EGO-WRAPPIN' found in database")
            else:
                logging.info("❌ EGO-WRAPPIN' not found in database")
            
            # 检查重复
            response = self.db.supabase.table("artists").select("name").execute()
            artists = response.data
            
            name_counts = {}
            for artist in artists:
                name = artist["name"]
                name_counts[name] = name_counts.get(name, 0) + 1
            
            duplicates = {name: count for name, count in name_counts.items() if count > 1}
            
            if duplicates:
                logging.info(f"❌ Still found {len(duplicates)} duplicate names:")
                for name, count in duplicates.items():
                    logging.info(f"  {name}: {count} entries")
            else:
                logging.info("✅ No duplicates remaining")
                
        except Exception as e:
            logging.error(f"❌ Error verifying fixes: {str(e)}")
    
    async def fix_all(self):
        """执行所有修复"""
        logging.info("=== Starting Artist Name Fixes ===")
        
        # 1. 修复 EGO-WRAPPIN' 名字
        await self.fix_egowrappin_name()
        
        # 2. 移除重复条目
        await self.remove_duplicates()
        
        # 3. 验证修复结果
        await self.verify_fixes()
        
        logging.info("=== Artist Name Fixes Complete ===")

async def main():
    fixer = ArtistNameFixer()
    await fixer.fix_all()

if __name__ == "__main__":
    asyncio.run(main()) 