import sys
from pathlib import Path

# Add project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from services.artist_db_service import artist_db_service

def check_artists_table_schema():
    """检查artists表的结构"""
    print("🔍 Checking artists table schema...")
    
    try:
        # 获取表结构信息
        response = artist_db_service.db.supabase.rpc(
            'get_table_columns', 
            {'table_name': 'artists'}
        ).execute()
        
        print("✅ Table schema retrieved successfully")
        print("Columns in artists table:")
        for column in response.data:
            print(f"  - {column['column_name']}: {column['data_type']}")
            
    except Exception as e:
        print(f"❌ Error getting schema: {e}")
        
        # 尝试另一种方法：获取一条记录看看字段
        print("\n🔍 Trying to get a sample record...")
        try:
            response = artist_db_service.db.supabase.table("artists").select("*").limit(1).execute()
            if response.data:
                sample_record = response.data[0]
                print("Sample record fields:")
                for key, value in sample_record.items():
                    print(f"  - {key}: {type(value).__name__}")
            else:
                print("No records found in artists table")
        except Exception as e2:
            print(f"❌ Error getting sample record: {e2}")

def check_wiki_fields():
    """检查Wiki相关字段"""
    print("\n🔍 Checking Wiki-related fields...")
    
    try:
        # 尝试更新一个不存在的字段来测试
        test_response = artist_db_service.db.supabase.table("artists").select(
            "id, name, wiki_extract, wiki_title, wiki_language"
        ).limit(1).execute()
        
        if test_response.data:
            sample = test_response.data[0]
            print("Available Wiki fields:")
            for field in ['wiki_extract', 'wiki_title', 'wiki_language']:
                if field in sample:
                    print(f"  ✅ {field}: {type(sample[field]).__name__}")
                else:
                    print(f"  ❌ {field}: NOT FOUND")
        else:
            print("No records found")
            
    except Exception as e:
        print(f"❌ Error checking Wiki fields: {e}")

if __name__ == "__main__":
    check_artists_table_schema()
    check_wiki_fields() 