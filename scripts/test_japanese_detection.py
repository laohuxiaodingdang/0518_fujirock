#!/usr/bin/env python3
"""
日文检测和翻译功能测试脚本（修复版）

这个脚本用于测试日文检测逻辑和翻译功能，
在运行完整翻译脚本之前进行验证。
"""

import asyncio
import logging
import sys
import re
import os
from pathlib import Path

# Add project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class JapaneseDetectionTester:
    """日文检测测试器（修复版）"""
    
    def __init__(self):
        # 更精确的日文检测正则表达式
        self.hiragana_pattern = re.compile(r'[\u3040-\u309F]')  # 平假名
        self.katakana_pattern = re.compile(r'[\u30A0-\u30FF]')  # 片假名
        self.kanji_pattern = re.compile(r'[\u4E00-\u9FAF]')     # 汉字
        
        # 专有名词识别模式（更精确）
        self.proper_noun_patterns = [
            r'\([^)]*[A-Za-z][^)]*\)',  # 括号内包含英文的
            r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b',  # 英文人名格式（单词边界）
            r'\b[A-Z]{2,}\b',  # 全大写缩写（单词边界）
            r'[0-9]{4}年',  # 年份
            r'[0-9]+月',   # 月份
            r'[0-9]+日',   # 日期
        ]

    def detect_japanese(self, text: str) -> bool:
        """
        更精确的日文检测
        主要依据：平假名和片假名的存在
        """
        if not text:
            return False
        
        # 检测平假名和片假名
        hiragana_count = len(self.hiragana_pattern.findall(text))
        katakana_count = len(self.katakana_pattern.findall(text))
        
        # 如果有平假名或片假名，很可能是日文
        if hiragana_count > 0 or katakana_count > 0:
            return True
        
        # 如果只有汉字，需要进一步判断
        kanji_count = len(self.kanji_pattern.findall(text))
        total_chars = len(text.replace(' ', '').replace('\n', ''))
        
        if total_chars == 0:
            return False
        
        # 检查是否有日文特有的表达方式
        japanese_indicators = [
            r'の',      # 日文助词
            r'は',      # 日文助词
            r'を',      # 日文助词
            r'に',      # 日文助词
            r'で',      # 日文助词
            r'と',      # 日文助词
            r'が',      # 日文助词
            r'から',    # 日文助词
            r'まで',    # 日文助词
            r'です',    # 日文敬语
            r'ます',    # 日文敬语
            r'である',  # 日文表达
        ]
        
        for indicator in japanese_indicators:
            if re.search(indicator, text):
                return True
        
        # 如果汉字占比很高且没有中文特征，可能是日文
        if kanji_count > 0:
            kanji_ratio = kanji_count / total_chars
            # 检查中文特征
            chinese_indicators = [
                r'的',      # 中文助词
                r'了',      # 中文助词
                r'在',      # 中文介词
                r'是',      # 中文系动词
                r'有',      # 中文动词
                r'和',      # 中文连词
                r'与',      # 中文连词
                r'及',      # 中文连词
                r'等',      # 中文等等
            ]
            
            has_chinese = any(re.search(indicator, text) for indicator in chinese_indicators)
            
            # 如果没有明显的中文特征且汉字占比高，可能是日文
            if not has_chinese and kanji_ratio > 0.3:
                return True
        
        return False

    def extract_proper_nouns(self, text: str) -> list:
        """提取文本中的专有名词（更精确）"""
        proper_nouns = []
        
        for pattern in self.proper_noun_patterns:
            matches = re.findall(pattern, text)
            proper_nouns.extend(matches)
        
        # 去重并过滤
        unique_nouns = list(set(proper_nouns))
        # 过滤掉过短的匹配和常见词
        common_words = {'The', 'This', 'That', 'His', 'Her', 'You', 'Tube', 'And', 'Or', 'But', 'In', 'On', 'At', 'To', 'For', 'Of', 'With'}
        filtered_nouns = [
            noun for noun in unique_nouns 
            if len(noun.strip()) > 1 and noun.strip() not in common_words
        ]
        
        return filtered_nouns

    def test_sample_texts(self):
        """测试示例文本"""
        # 测试用例
        test_cases = [
            {
                "name": "日文艺术家介绍（来自你的截图）",
                "text": "フィンランド出身の5人組ロックバンド、US(アス)。USはヴォーカリスト／ギタリストで主なソングライターのテオ・ヒルヴォネン(Teo Hirvonen)とベーシストのラスムス・ルオナコスキ(Rasmus Ruonakoski)が高校で結成したバンドが始まり。",
                "expected": True
            },
            {
                "name": "中文文本",
                "text": "杜娃·黎波，是一名英国及阿尔巴尼亚的创作歌手。她的音乐生涯起步于14岁，当时她在YouTube上翻唱粉红佳人和妮莉·费塔朵等艺人的歌曲。",
                "expected": False
            },
            {
                "name": "英文文本",
                "text": "Post Malone is an American singer, rapper, songwriter, and record producer. His music blends various genres including hip hop, R&B, pop, trap, and rock.",
                "expected": False
            },
            {
                "name": "混合文本（少量日文）",
                "text": "This is mostly English text with some Japanese characters like こんにちは.",
                "expected": True
            },
            {
                "name": "纯日文（片假名）",
                "text": "ロックバンド、アーティスト、ミュージック",
                "expected": True
            },
            {
                "name": "空文本",
                "text": "",
                "expected": False
            }
        ]
        
        print("=== 日文检测测试（优化版） ===\n")
        
        correct_count = 0
        
        for i, case in enumerate(test_cases, 1):
            print(f"测试用例 {i}: {case['name']}")
            print(f"文本: {case['text'][:100]}{'...' if len(case['text']) > 100 else ''}")
            
            is_japanese = self.detect_japanese(case['text'])
            proper_nouns = self.extract_proper_nouns(case['text'])
            expected = case['expected']
            
            result_icon = "✅" if is_japanese == expected else "❌"
            correct_count += 1 if is_japanese == expected else 0
            
            print(f"是否为日文: {'是' if is_japanese else '否'} {result_icon}")
            print(f"预期结果: {'是' if expected else '否'}")
            print(f"检测到的专有名词: {proper_nouns if proper_nouns else '无'}")
            print("-" * 50)
        
        print(f"检测准确率: {correct_count}/{len(test_cases)} ({correct_count/len(test_cases)*100:.1f}%)\n")

def test_environment_variables():
    """测试环境变量配置"""
    print("=== 环境变量配置测试 ===")
    
    # 检查必要的环境变量
    required_vars = {
        'ARK_API_KEY': 'DeepSeek API密钥',
        'SUPABASE_URL': 'Supabase数据库URL',
        'SUPABASE_ANON_KEY': 'Supabase匿名密钥'
    }
    
    all_configured = True
    
    for var_name, description in required_vars.items():
        value = os.getenv(var_name)
        if value:
            print(f"✅ {var_name}: 已配置 ({description})")
        else:
            print(f"❌ {var_name}: 未配置 ({description})")
            all_configured = False
    
    if all_configured:
        print("\n✅ 所有必要的环境变量都已配置，可以运行翻译脚本")
    else:
        print("\n⚠️ 部分环境变量未配置，请在 .env 文件中设置")
        print("示例:")
        print("ARK_API_KEY=your_deepseek_api_key")
        print("SUPABASE_URL=your_supabase_url")
        print("SUPABASE_ANON_KEY=your_supabase_key")

def test_dependencies():
    """测试依赖包"""
    print("\n=== 依赖包测试 ===")
    
    required_packages = [
        ('openai', 'OpenAI客户端'),
        ('asyncio', 'Python异步库'),
        ('re', 'Python正则表达式'),
        ('json', 'Python JSON库'),
        ('pathlib', 'Python路径库')
    ]
    
    missing_packages = []
    
    for package, description in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}: 已安装 ({description})")
        except ImportError:
            print(f"❌ {package}: 未安装 ({description})")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️ 缺少依赖包: {', '.join(missing_packages)}")
        print("请运行: pip install openai")
    else:
        print("\n✅ 所有必要的依赖包都已安装")

def test_file_structure():
    """测试文件结构"""
    print("\n=== 文件结构测试 ===")
    
    expected_files = [
        'backend/config.py',
        'backend/services/artist_db_service.py',
        'scripts/translate_japanese_descriptions.py'
    ]
    
    all_exists = True
    
    for file_path in expected_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"✅ {file_path}: 存在")
        else:
            print(f"❌ {file_path}: 不存在")
            all_exists = False
    
    if all_exists:
        print("\n✅ 所有必要的文件都存在")
    else:
        print("\n⚠️ 部分文件缺失，可能影响翻译功能")

async def main():
    """主测试函数"""
    print("=== 日文检测和翻译功能测试（修复版） ===\n")
    
    # 创建测试器
    tester = JapaneseDetectionTester()
    
    # 运行所有测试
    tester.test_sample_texts()
    test_environment_variables()
    test_dependencies()
    test_file_structure()
    
    print("\n=== 测试完成 ===")
    print("如果大部分测试通过，你可以尝试运行翻译脚本：")
    print("python scripts/translate_japanese_descriptions.py")
    print("\n如果遇到问题，请检查上述测试结果中的错误信息。")

if __name__ == "__main__":
    asyncio.run(main())