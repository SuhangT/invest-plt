"""
测试数据抓取重试机制
"""
from app import app
from data_fetcher import DataFetcher
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_retry_mechanism():
    """测试重试机制"""
    with app.app_context():
        # 创建数据抓取器，设置较短的重试次数用于测试
        fetcher = DataFetcher(max_retries=3, min_delay=1, max_delay=3)
        
        print("=" * 60)
        print("测试数据抓取重试机制")
        print("=" * 60)
        print()
        
        # 测试1: 获取指数列表
        print("测试1: 获取指数列表")
        print("-" * 60)
        result = fetcher.fetch_all_indices()
        print(f"结果: {'成功' if result else '失败'}")
        print()
        
        # 测试2: 获取指数历史数据（中证800）
        print("测试2: 获取中证800历史数据")
        print("-" * 60)
        result = fetcher.fetch_index_history('000906', '20241001', '20241014')
        print(f"结果: {'成功' if result else '失败'}")
        print()
        
        # 测试3: 获取成份股数据
        print("测试3: 获取中证800成份股")
        print("-" * 60)
        result = fetcher.fetch_index_constituents('000906')
        print(f"结果: {'成功' if result else '失败'}")
        print()
        
        # 测试4: 获取国债收益率
        print("测试4: 获取国债收益率")
        print("-" * 60)
        result = fetcher.fetch_bond_yield()
        print(f"结果: {'成功' if result else '失败'}")
        print()
        
        print("=" * 60)
        print("测试完成")
        print("=" * 60)

if __name__ == '__main__':
    test_retry_mechanism()
