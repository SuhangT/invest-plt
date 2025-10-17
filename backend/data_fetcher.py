import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from models import db, Index, IndexHistory, IndexConstituent, StockFinancial, BondYield
import time
import random
import logging
from functools import wraps

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def retry_on_failure(max_retries=10, min_delay=2, max_delay=10):
    """
    重试装饰器：API调用失败时自动重试
    
    Args:
        max_retries: 最大重试次数
        min_delay: 最小延迟时间（秒）
        max_delay: 最大延迟时间（秒）
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    # 执行函数
                    result = func(*args, **kwargs)
                    
                    # 如果返回False，也视为失败
                    if result is False and attempt < max_retries - 1:
                        raise Exception("Function returned False")
                    
                    return result
                    
                except Exception as e:
                    last_exception = e
                    
                    if attempt < max_retries - 1:
                        # 计算随机延迟时间
                        delay = random.uniform(min_delay, max_delay)
                        logger.warning(
                            f"[重试 {attempt + 1}/{max_retries}] {func.__name__} 失败: {str(e)}, "
                            f"{delay:.1f}秒后重试..."
                        )
                        time.sleep(delay)
                    else:
                        logger.error(
                            f"[失败] {func.__name__} 已重试 {max_retries} 次仍然失败: {str(e)}"
                        )
            
            # 所有重试都失败，返回False或抛出异常
            return False
        
        return wrapper
    return decorator


class DataFetcher:
    """数据抓取类 - 带重试机制"""
    
    def __init__(self, max_retries=10, min_delay=2, max_delay=10):
        """
        初始化数据抓取器
        
        Args:
            max_retries: 最大重试次数
            min_delay: 最小延迟时间（秒）
            max_delay: 最大延迟时间（秒）
        """
        self.max_retries = max_retries
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.base_delay = 0.5  # 基础API调用间隔（秒）
    
    def _random_delay(self):
        """随机延迟，避免频率限制"""
        delay = random.uniform(self.base_delay, self.base_delay + 1.0)
        time.sleep(delay)
    
    @retry_on_failure(max_retries=10, min_delay=3, max_delay=10)
    def _fetch_indices_data(self):
        """内部方法：获取指数数据（带重试）"""
        return ak.index_csindex_all()
    
    def fetch_all_indices(self):
        """获取所有中证指数列表"""
        try:
            logger.info("开始获取所有中证指数列表...")
            # 获取所有中证指数（带重试机制）
            df = self._fetch_indices_data()
            
            if df is False or df is None or df.empty:
                logger.error("获取指数列表失败")
                return False
            
            indices = []
            for _, row in df.iterrows():
                index_code = str(row.get('指数代码', '')).strip()
                index_name = str(row.get('指数简称', '')).strip()
                index_name_full = str(row.get('指数全称', '')).strip()
                
                if not index_code:
                    continue
                
                # 检查是否已存在
                existing = Index.query.filter_by(code=index_code).first()
                if existing:
                    existing.name = index_name
                    existing.name_full = index_name_full
                    existing.updated_at = datetime.now()
                else:
                    index = Index(
                        code=index_code,
                        name=index_name,
                        name_full=index_name_full,
                        is_favorite=False,
                        manual_weight=1.0
                    )
                    indices.append(index)
            
            if indices:
                db.session.bulk_save_objects(indices)
                db.session.commit()
            
            logger.info(f"成功获取 {len(df)} 个指数，新增 {len(indices)} 个")
            return True
            
        except Exception as e:
            logger.error(f"获取指数列表失败: {str(e)}")
            db.session.rollback()
            return False
    
    @retry_on_failure(max_retries=10, min_delay=3, max_delay=10)
    def _fetch_index_history_data(self, index_code, start_date, end_date):
        """内部方法：获取指数历史数据（带重试）"""
        df = ak.stock_zh_index_hist_csindex(
            symbol=index_code,
            start_date=start_date,
            end_date=end_date
        )
        if df.empty:
            raise Exception(f"指数 {index_code} 返回空数据")
        return df
    
    def fetch_index_history(self, index_code, start_date=None, end_date=None):
        """获取指数历史数据"""
        try:
            if not end_date:
                end_date = datetime.now().strftime('%Y%m%d')
            
            if not start_date:
                # 默认获取近10年数据
                start_date = (datetime.now() - timedelta(days=3650)).strftime('%Y%m%d')
            
            logger.info(f"获取指数 {index_code} 历史数据: {start_date} - {end_date}")
            
            # 获取指数对象
            index = Index.query.filter_by(code=index_code).first()
            if not index:
                logger.warning(f"指数 {index_code} 不存在")
                return False
            
            # 调用akshare接口（带重试）
            df = self._fetch_index_history_data(index_code, start_date, end_date)
            
            if df is False or df is None:
                logger.error(f"指数 {index_code} 历史数据获取失败")
                return False
            
            # 数据清洗和入库
            records = []
            for _, row in df.iterrows():
                date_str = str(row.get('日期', ''))
                if not date_str:
                    continue
                
                try:
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                except:
                    continue
                
                # 检查是否已存在
                existing = IndexHistory.query.filter_by(
                    index_id=index.id,
                    date=date_obj
                ).first()
                
                if existing:
                    # 更新现有记录
                    existing.open = float(row.get('开盘', 0)) if pd.notna(row.get('开盘')) else None
                    existing.high = float(row.get('最高', 0)) if pd.notna(row.get('最高')) else None
                    existing.low = float(row.get('最低', 0)) if pd.notna(row.get('最低')) else None
                    existing.close = float(row.get('收盘', 0)) if pd.notna(row.get('收盘')) else None
                    existing.volume = float(row.get('成交量', 0)) if pd.notna(row.get('成交量')) else None
                    existing.amount = float(row.get('成交金额', 0)) if pd.notna(row.get('成交金额')) else None
                    existing.pe_ttm = float(row.get('滚动市盈率', 0)) if pd.notna(row.get('滚动市盈率')) else None
                    existing.sample_count = int(row.get('样本数量', 0)) if pd.notna(row.get('样本数量')) else None
                else:
                    # 新增记录
                    record = IndexHistory(
                        index_id=index.id,
                        date=date_obj,
                        open=float(row.get('开盘', 0)) if pd.notna(row.get('开盘')) else None,
                        high=float(row.get('最高', 0)) if pd.notna(row.get('最高')) else None,
                        low=float(row.get('最低', 0)) if pd.notna(row.get('最低')) else None,
                        close=float(row.get('收盘', 0)) if pd.notna(row.get('收盘')) else None,
                        volume=float(row.get('成交量', 0)) if pd.notna(row.get('成交量')) else None,
                        amount=float(row.get('成交金额', 0)) if pd.notna(row.get('成交金额')) else None,
                        pe_ttm=float(row.get('滚动市盈率', 0)) if pd.notna(row.get('滚动市盈率')) else None,
                        sample_count=int(row.get('样本数量', 0)) if pd.notna(row.get('样本数量')) else None
                    )
                    records.append(record)
            
            if records:
                db.session.bulk_save_objects(records)
            
            db.session.commit()
            logger.info(f"指数 {index_code} 历史数据入库成功，共 {len(df)} 条")
            
            self._random_delay()
            return True
            
        except Exception as e:
            logger.error(f"获取指数 {index_code} 历史数据失败: {str(e)}")
            db.session.rollback()
            return False
    
    @retry_on_failure(max_retries=10, min_delay=3, max_delay=10)
    def _fetch_constituents_data(self, index_code):
        """内部方法：获取成份股数据（带重试）"""
        df = ak.index_stock_cons_weight_csindex(symbol=index_code)
        if df.empty:
            raise Exception(f"指数 {index_code} 返回空成份股数据")
        return df
    
    def fetch_index_constituents(self, index_code):
        """获取指数成份股及权重"""
        try:
            logger.info(f"获取指数 {index_code} 成份股...")
            
            index = Index.query.filter_by(code=index_code).first()
            if not index:
                logger.warning(f"指数 {index_code} 不存在")
                return False
            
            # 获取成份股权重（带重试）
            df = self._fetch_constituents_data(index_code)
            
            if df is False or df is None:
                logger.error(f"指数 {index_code} 成份股数据获取失败")
                return False
            
            # 解析日期
            date_str = str(df.iloc[0].get('日期', ''))
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            except:
                date_obj = datetime.now().date()
            
            # 删除该日期的旧数据
            IndexConstituent.query.filter_by(
                index_id=index.id,
                date=date_obj
            ).delete()
            
            # 插入新数据
            records = []
            for _, row in df.iterrows():
                stock_code = str(row.get('成分券代码', '')).strip()
                if not stock_code:
                    continue
                
                record = IndexConstituent(
                    index_id=index.id,
                    date=date_obj,
                    stock_code=stock_code,
                    stock_name=str(row.get('成分券名称', '')).strip(),
                    stock_name_en=str(row.get('成分券英文名称', '')).strip(),
                    exchange=str(row.get('交易所', '')).strip(),
                    weight=float(row.get('权重', 0)) if pd.notna(row.get('权重')) else None
                )
                records.append(record)
            
            if records:
                db.session.bulk_save_objects(records)
                db.session.commit()
            
            logger.info(f"指数 {index_code} 成份股入库成功，共 {len(records)} 只")
            
            self._random_delay()
            return True
            
        except Exception as e:
            logger.error(f"获取指数 {index_code} 成份股失败: {str(e)}")
            db.session.rollback()
            return False
    
    @retry_on_failure(max_retries=10, min_delay=3, max_delay=10)
    def _fetch_financials_data(self, report_date):
        """内部方法：获取财务数据（带重试）"""
        df1 = ak.stock_lrb_em(date=report_date)
        df2 = ak.stock_zcfz_em(date=report_date)
        if df1.empty or df2.empty:
            raise Exception(f"报告期 {report_date} 返回空数据")
        # 按照股票代码横向合并
        df1 = df1[['股票代码', '股票简称', '净利润']]
        df2 = df2[['股票代码', '股东权益合计']]
        df = pd.merge(df1, df2, on='股票代码')
        return df
    
    def fetch_stock_financials(self, report_date):
        """获取股票财务数据
        
        Args:
            report_date: 报告期，格式如 "20240331"
        """
        try:
            logger.info(f"获取 {report_date} 财务数据...")
            
            # 调用akshare接口（带重试）
            df = self._fetch_financials_data(report_date)
            
            if df is False or df is None:
                logger.error(f"报告期 {report_date} 财务数据获取失败")
                return False
            
            records = []
            for _, row in df.iterrows():
                stock_code = str(row.get('股票代码', '')).strip()
                if not stock_code:
                    continue
                
                # 解析报告期
                try:
                    date_obj = datetime.strptime(report_date, '%Y%m%d').date()
                except:
                    continue
                
                # 检查是否已存在
                existing = StockFinancial.query.filter_by(
                    stock_code=stock_code,
                    report_date=date_obj
                ).first()
                
                roe_val = row.get('净资产收益率')
                stock_name = str(row.get('股票简称', '')).strip()
                net_profit = float(row.get('净利润', 0)) if pd.notna(row.get('净利润')) else None
                equity = float(row.get('股东权益合计', 0)) if pd.notna(row.get('股东权益合计')) else None

                if pd.notna(roe_val):
                    roe_val = float(roe_val)
                else:
                    roe_val = None

                if existing:
                    existing.stock_name = stock_name
                    existing.net_profit = net_profit
                    existing.equity = equity
                    existing.roe = roe_val
                else:
                    record = StockFinancial(
                        stock_code=stock_code,
                        stock_name=stock_name,
                        report_date=date_obj,
                        net_profit=net_profit,
                        equity=equity,
                        roe=roe_val
                    )
                    records.append(record)

            if records:
                db.session.bulk_save_objects(records)
            
            db.session.commit()
            logger.info(f"财务数据入库成功，共 {len(df)} 条")
            
            self._random_delay()
            return True
            
        except Exception as e:
            logger.error(f"获取财务数据失败: {str(e)}")
            db.session.rollback()
            return False
    
    @retry_on_failure(max_retries=10, min_delay=3, max_delay=10)
    def _fetch_bond_yield_data(self):
        """内部方法：获取国债数据（带重试）"""
        df = ak.bond_zh_us_rate()
        if df.empty:
            raise Exception("国债收益率返回空数据")
        return df
    
    def fetch_bond_yield(self, start_date=None, end_date=None):
        """获取10年期国债收益率"""
        try:
            logger.info("获取10年期国债收益率...")
            
            # 使用akshare获取国债收益率数据（带重试）
            df = self._fetch_bond_yield_data()
            
            if df is False or df is None:
                logger.error("国债收益率数据获取失败")
                return False
            
            # 筛选10年期数据
            df_10y = df[['日期', '中国国债收益率10年']]
            
            records = []
            for _, row in df_10y.iterrows():
                date_str = str(row.get('日期', ''))
                if not date_str:
                    continue
                
                try:
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                except:
                    continue
                
                # 检查日期范围
                if start_date and date_obj < datetime.strptime(start_date, '%Y%m%d').date():
                    continue
                if end_date and date_obj > datetime.strptime(end_date, '%Y%m%d').date():
                    continue
                
                # 检查是否已存在
                existing = BondYield.query.filter_by(date=date_obj).first()
                
                yield_val = row.get('中国国债收益率10年')
                if pd.notna(yield_val):
                    yield_val = float(yield_val)
                else:
                    yield_val = None
                
                if existing:
                    existing.yield_10y = yield_val
                else:
                    record = BondYield(
                        date=date_obj,
                        yield_10y=yield_val
                    )
                    records.append(record)
            
            if records:
                db.session.bulk_save_objects(records)
            
            db.session.commit()
            logger.info(f"国债收益率数据入库成功，共 {len(records)} 条")
            
            return True
            
        except Exception as e:
            logger.error(f"获取国债收益率失败: {str(e)}")
            db.session.rollback()
            return False
    
    def fetch_latest_financials(self):
        """获取最新季度财务数据"""
        try:
            # 获取最近5个季度的财务数据
            now = datetime.now()
            year = now.year
            
            # 确定最近的报告期
            if now.month >= 10:
                quarters = [f"{year}0930", f"{year}0630", f"{year}0331", f"{year-1}1231", f"{year-1}0930"]
            elif now.month >= 7:
                quarters = [f"{year}0630", f"{year}0331", f"{year-1}1231", f"{year-1}0930", f"{year-1}0630"]
            elif now.month >= 4:
                quarters = [f"{year}0331", f"{year-1}1231", f"{year-1}0930", f"{year-1}0630", f"{year-1}0331"]
            else:
                quarters = [f"{year-1}1231", f"{year-1}0930", f"{year-1}0630", f"{year-1}0331", f"{year-2}1231"]
            
            for quarter in quarters:
                self.fetch_stock_financials(quarter)
                self._random_delay()
            
            return True
            
        except Exception as e:
            logger.error(f"获取最新财务数据失败: {str(e)}")
            return False
