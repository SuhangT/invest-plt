import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from models import (db, Index, IndexHistory, IndexConstituent, StockFinancial, 
                    BondYield, CalculatedMetrics, StockBondRatio)
import logging
from sqlalchemy import func, extract, case

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Calculator:
    """核心计算逻辑类"""
    
    # 估值分位区间配置
    PERCENTILE_RANGES = [
        (0, 10, 40),
        (10, 20, 35),
        (20, 35, 30),
        (35, 50, 25),
        (50, 65, 20),
        (65, 80, 15),
        (80, 90, 10),
        (90, 100, 5)
    ]
    
    def __init__(self):
        pass
    
    def get_percentile_range_and_score(self, percentile):
        """根据分位数获取区间和初始分数
        
        Args:
            percentile: 分位数（0-100）
            
        Returns:
            tuple: (区间字符串, 初始分数)
        """
        if percentile is None or np.isnan(percentile):
            return None, 0
        
        for min_p, max_p, score in self.PERCENTILE_RANGES:
            if min_p <= percentile < max_p:
                return f"{min_p}%-{max_p}%", score
        
        # 处理边界情况
        if percentile >= 90:
            return "90%-100%", 5
        
        return "0%-10%", 40
    
    def calculate_roe_weight(self, roe):
        """计算ROE权重
        
        ROE=10%时权重为1，每±1%调整0.1
        ROE≤0时权重置0
        
        Args:
            roe: 净资产收益率（%）
            
        Returns:
            float: ROE权重
        """
        if roe is None or np.isnan(roe) or roe <= 0:
            return 1.0  # 缺失值或≤0时权重为1（根据需求）
        
        # ROE=10%时权重为1，每±1%调整0.1
        weight = 1.0 + (roe - 10) * 0.1
        
        # 权重不能为负
        return max(0, weight)
    
    def calculate_index_weighted_roe(self, index_id, date=None):
        """计算指数加权ROE
        
        Args:
            index_id: 指数ID
            date: 日期，默认为最新日期
            
        Returns:
            float: 加权ROE
        """
        try:

            # 获取最新成份股日期
            latest_constituent = IndexConstituent.query.filter_by(
                index_id=index_id
            ).order_by(IndexConstituent.date.desc()).first()

            if not latest_constituent:
                return None

            # 获取成分股更新的最新日期
            cons_date = latest_constituent.date
            
            # 获取成份股列表
            constituents = IndexConstituent.query.filter_by(
                index_id=index_id,
                date=cons_date
            ).all()
            
            if not constituents:
                return None
            
            # 计算加权ROE
            total_weight = 0
            weighted_roe_sum = 0
            
            for constituent in constituents:
                # 获取该股票近五季度的财务数据
                financial = StockFinancial.query.filter_by(
                    stock_code=constituent.stock_code
                ).order_by(StockFinancial.report_date.desc()).all()[:5]

                # 计算net_profit总和（处理None）
                total_net_profit = sum(
                    item.net_profit if item.net_profit is not None else 0
                    for item in financial
                )

                # 计算equity平均值（处理None和空列表）
                equity_values = [item.equity for item in financial if item.equity is not None]
                avg_equity = sum(equity_values) / len(equity_values) if equity_values else None

                weight = constituent.weight if constituent.weight else 0
                roe = total_net_profit / avg_equity if avg_equity is not None else None

                weighted_roe_sum += roe * weight
                total_weight += weight
            
            if total_weight == 0:
                return None
            
            return weighted_roe_sum / total_weight
            
        except Exception as e:
            logger.error(f"计算指数 {index_id} 加权ROE失败: {str(e)}")
            return None
    
    def calculate_percentile(self, index_id, metric='pe', lookback_days=3650):
        """计算指标分位数
        
        Args:
            index_id: 指数ID
            metric: 指标类型，'pe' or 'pb'
            lookback_days: 回溯天数，默认10年（3650天）
            
        Returns:
            float: 分位数（0-100）
        """
        try:
            # 获取历史数据
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=lookback_days)
            
            # 获取指数成立日期（第一条数据日期）
            first_record = IndexHistory.query.filter_by(
                index_id=index_id
            ).order_by(IndexHistory.date.asc()).first()
            
            if not first_record:
                return None
            
            # 如果成立不足10年，使用成立至今数据
            if first_record.date > start_date:
                start_date = first_record.date
            
            # 查询历史数据
            history = IndexHistory.query.filter(
                IndexHistory.index_id == index_id,
                IndexHistory.date >= start_date,
                IndexHistory.date <= end_date
            ).order_by(IndexHistory.date.asc()).all()
            
            if not history:
                return None
            
            # 提取指标值
            if metric == 'pe':
                values = [h.pe_ttm for h in history if h.pe_ttm is not None and h.pe_ttm > 0]
            elif metric == 'pb':
                values = [h.pb for h in history if h.pb is not None and h.pb > 0]
            else:
                return None
            
            if not values:
                return None
            
            # 获取最新值
            latest = history[-1]
            current_value = latest.pe_ttm if metric == 'pe' else latest.pb
            
            if current_value is None or current_value <= 0:
                return None
            
            # 计算分位数
            percentile = (np.sum(np.array(values) <= current_value) / len(values)) * 100
            
            return percentile
            
        except Exception as e:
            logger.error(f"计算指数 {index_id} {metric} 分位数失败: {str(e)}")
            return None
    
    def calculate_stock_bond_ratio(self, date=None, skip_percentile=False):
        """计算股债性价比
        
        股债性价比 = 1/中证800市盈率 - 10年国债收益率
        
        Args:
            date: 日期，默认为最新日期
            skip_percentile: 是否跳过分位数计算（用于历史数据计算）
            
        Returns:
            dict: 包含计算结果的字典
        """
        try:
            if not date:
                date = (datetime.now() - timedelta(days=1)).date()
            
            # 获取中证800（代码000906）的市盈率
            csi800 = Index.query.filter_by(code='000906').first()
            if not csi800:
                logger.warning("未找到中证800指数")
                return None
            
            # 获取最新PE数据
            latest_history = IndexHistory.query.filter(
                IndexHistory.index_id == csi800.id,
                IndexHistory.date <= date
            ).order_by(IndexHistory.date.desc()).first()
            
            if not latest_history or not latest_history.pe_ttm:
                logger.warning(f"未找到中证800市盈率数据 (date={date})")
                return None
            
            # 获取10年国债收益率
            bond_yield = BondYield.query.filter(
                BondYield.date <= date
            ).order_by(BondYield.date.desc()).first()
            
            if not bond_yield or not bond_yield.yield_10y:
                logger.warning(f"未找到10年国债收益率数据 (date={date})")
                return None
            
            # 计算股债性价比
            pe = latest_history.pe_ttm
            bond_rate = bond_yield.yield_10y / 100  # 转换为小数
            ratio = (1 / pe) - bond_rate
            
            # 计算近10年分位数
            percentile = 50  # 默认值
            if not skip_percentile:
                end_date = date
                start_date = date - timedelta(days=3650)
                
                # 获取历史股债性价比数据
                historical_ratios = StockBondRatio.query.filter(
                    StockBondRatio.date >= start_date,
                    StockBondRatio.date <= end_date
                ).all()
                
                ratio_values = [r.ratio for r in historical_ratios if r.ratio is not None]
                ratio_values.append(ratio)  # 包含当前值
                
                if len(ratio_values) > 1:
                    percentile = (np.sum(np.array(ratio_values) <= ratio) / len(ratio_values)) * 100
            
            # 股票配置比例 = 分位数
            stock_allocation = percentile
            
            result = {
                'date': date,
                'csi800_pe': pe,
                'bond_yield_10y': bond_yield.yield_10y,
                'ratio': ratio,
                'percentile_10y': percentile,
                'stock_allocation': stock_allocation
            }
            
            # 保存到数据库
            existing = StockBondRatio.query.filter_by(date=date).first()
            if existing:
                existing.csi800_pe = pe
                existing.bond_yield_10y = bond_yield.yield_10y
                existing.ratio = ratio
                existing.percentile_10y = percentile
                existing.stock_allocation = stock_allocation
            else:
                record = StockBondRatio(
                    date=date,
                    csi800_pe=pe,
                    bond_yield_10y=bond_yield.yield_10y,
                    ratio=ratio,
                    percentile_10y=percentile,
                    stock_allocation=stock_allocation
                )
                db.session.add(record)
            
            db.session.commit()
            
            return result
            
        except Exception as e:
            logger.error(f"计算股债性价比失败: {str(e)}")
            db.session.rollback()
            return None
    
    def calculate_historical_stock_bond_ratio(self):
        """计算近10年历史股债性价比数据"""
        try:
            logger.info("开始计算近10年历史股债性价比...")
            
            # 获取中证800指数
            csi800 = Index.query.filter_by(code='000906').first()
            if not csi800:
                logger.error("未找到中证800指数")
                return False
            
            # 获取近10年的所有历史数据日期
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=3650)
            
            # 获取所有有PE数据的日期
            history_records = IndexHistory.query.filter(
                IndexHistory.index_id == csi800.id,
                IndexHistory.date >= start_date,
                IndexHistory.date <= end_date,
                IndexHistory.pe_ttm.isnot(None)
            ).order_by(IndexHistory.date.asc()).all()
            
            if not history_records:
                logger.warning("没有找到中证800历史数据")
                return False
            
            logger.info(f"找到 {len(history_records)} 条历史数据，开始计算...")
            
            # 第一遍：计算所有日期的股债性价比（不计算分位数）
            for record in history_records:
                self.calculate_stock_bond_ratio(record.date, skip_percentile=True)
            
            # 第二遍：重新计算所有日期的分位数
            logger.info("开始计算分位数...")
            all_ratios = StockBondRatio.query.filter(
                StockBondRatio.date >= start_date,
                StockBondRatio.date <= end_date
            ).order_by(StockBondRatio.date.asc()).all()
            
            for ratio_record in all_ratios:
                # 获取该日期之前10年的数据
                lookback_start = ratio_record.date - timedelta(days=3650)
                
                historical_ratios = StockBondRatio.query.filter(
                    StockBondRatio.date >= lookback_start,
                    StockBondRatio.date <= ratio_record.date
                ).all()
                
                ratio_values = [r.ratio for r in historical_ratios if r.ratio is not None]
                
                if len(ratio_values) > 1:
                    percentile = (np.sum(np.array(ratio_values) <= ratio_record.ratio) / len(ratio_values)) * 100
                    ratio_record.percentile_10y = percentile
                    ratio_record.stock_allocation = percentile
            
            db.session.commit()
            logger.info(f"成功计算 {len(all_ratios)} 条历史股债性价比数据")
            return True
            
        except Exception as e:
            logger.error(f"计算历史股债性价比失败: {str(e)}")
            db.session.rollback()
            return False
    
    def calculate_index_metrics(self, index_id, date=None):
        """计算单个指数的所有指标
        
        Args:
            index_id: 指数ID
            date: 日期，默认为最新日期
            
        Returns:
            dict: 计算结果
        """
        try:
            if not date:
                date = datetime.now().date()
            
            # 获取指数信息
            index = Index.query.get(index_id)
            if not index:
                return None
            
            # 只计算自选指数
            if not index.is_favorite:
                return None
            
            # 计算PE和PB分位数
            pe_percentile = self.calculate_percentile(index_id, 'pe')
            pb_percentile = self.calculate_percentile(index_id, 'pb')
            
            # 使用PE分位数作为主要依据（也可以改为PB或综合）
            main_percentile = pe_percentile if pe_percentile is not None else pb_percentile
            
            if main_percentile is None:
                return None
            
            # 获取分位区间和初始分数
            percentile_range, initial_score = self.get_percentile_range_and_score(main_percentile)
            
            # 计算加权ROE
            logger.info('开始计算加权ROE')
            weighted_roe = self.calculate_index_weighted_roe(index_id, date)
            
            # 计算ROE权重
            roe_weight = self.calculate_roe_weight(weighted_roe)
            
            # 获取人为权重
            manual_weight = index.manual_weight if index.manual_weight else 1.0
            
            # 计算综合权重和综合分数
            composite_weight = roe_weight * manual_weight
            composite_score = initial_score * composite_weight
            
            # 检查操作信号（需要前一日数据）
            previous_date = date - timedelta(days=1)
            previous_metrics = CalculatedMetrics.query.filter_by(
                index_id=index_id,
                date=previous_date
            ).first()
            
            operation_signal = None
            operation_percent = None
            previous_range = None
            
            if previous_metrics and previous_metrics.percentile_range:
                previous_range = previous_metrics.percentile_range
                
                # 解析区间
                prev_min, prev_max = self._parse_range(previous_range)
                curr_min, curr_max = self._parse_range(percentile_range)
                
                # 向上突破（减仓）
                if main_percentile > prev_max:
                    operation_signal = 'reduce'
                    # 计算建议减仓比例（简化：按突破幅度）
                    operation_percent = min(20, (main_percentile - prev_max) * 2)
                
                # 向下突破且达到上一区间均值（加仓）
                elif main_percentile < prev_min:
                    # 检查是否达到上一区间均值
                    upper_range_mean = (prev_min + prev_max) / 2
                    if main_percentile <= upper_range_mean:
                        operation_signal = 'add'
                        operation_percent = min(20, (prev_min - main_percentile) * 2)
            
            result = {
                'index_id': index_id,
                'date': date,
                'pe_percentile': pe_percentile,
                'pb_percentile': pb_percentile,
                'weighted_roe': weighted_roe,
                'roe_weight': roe_weight,
                'percentile_range': percentile_range,
                'initial_score': initial_score,
                'composite_weight': composite_weight,
                'composite_score': composite_score,
                'target_position': 0,  # 稍后计算
                'operation_signal': operation_signal,
                'operation_percent': operation_percent,
                'previous_range': previous_range
            }
            
            # 保存到数据库
            existing = CalculatedMetrics.query.filter_by(
                index_id=index_id,
                date=date
            ).first()
            
            if existing:
                for key, value in result.items():
                    if key not in ['index_id', 'date']:
                        setattr(existing, key, value)
            else:
                record = CalculatedMetrics(**result)
                db.session.add(record)
            
            db.session.commit()
            
            return result
            
        except Exception as e:
            logger.error(f"计算指数 {index_id} 指标失败: {str(e)}")
            db.session.rollback()
            return None
    
    def _parse_range(self, range_str):
        """解析区间字符串
        
        Args:
            range_str: 如 "10%-20%"
            
        Returns:
            tuple: (min, max)
        """
        try:
            parts = range_str.replace('%', '').split('-')
            return float(parts[0]), float(parts[1])
        except:
            return 0, 100
    
    def calculate_all_positions(self, date=None):
        """计算所有自选指数的目标仓位
        
        根据综合分数占比分配
        
        Args:
            date: 日期，默认为最新日期
        """
        try:
            if not date:
                date = datetime.now().date()
            
            # 获取所有自选指数的计算指标
            metrics = CalculatedMetrics.query.join(Index).filter(
                CalculatedMetrics.date == date,
                Index.is_favorite == True
            ).all()
            
            if not metrics:
                logger.warning("无自选指数计算数据")
                return
            
            # 计算总分
            total_score = sum(m.composite_score for m in metrics if m.composite_score)
            
            if total_score == 0:
                logger.warning("总分为0，无法分配仓位")
                return
            
            # 分配仓位
            for metric in metrics:
                if metric.composite_score:
                    target_position = (metric.composite_score / total_score) * 100
                    metric.target_position = target_position
            
            db.session.commit()
            logger.info(f"成功计算 {len(metrics)} 个指数的目标仓位")
            
        except Exception as e:
            logger.error(f"计算目标仓位失败: {str(e)}")
            db.session.rollback()
    
    def run_daily_calculation(self, date=None):
        """执行每日计算任务
        
        Args:
            date: 日期，默认为今天
        """
        try:
            if not date:
                date = (datetime.now() - timedelta(days=1)).date()
            
            logger.info(f"开始执行 {date} 的每日计算...")
            
            # 1. 计算股债性价比
            stock_bond_result = self.calculate_stock_bond_ratio(date)
            if stock_bond_result:
                logger.info(f"股债性价比: {stock_bond_result['ratio']:.4f}, "
                          f"分位数: {stock_bond_result['percentile_10y']:.2f}%, "
                          f"股票配置: {stock_bond_result['stock_allocation']:.2f}%")
            
            # 2. 计算所有自选指数的指标
            favorite_indices = Index.query.filter_by(is_favorite=True).all()
            
            for index in favorite_indices:
                result = self.calculate_index_metrics(index.id, date)
                if result:
                    logger.info(f"指数 {index.name} ({index.code}): "
                              f"PE分位={result['pe_percentile']:.2f}%, "
                              f"区间={result['percentile_range']}, "
                              f"综合分数={result['composite_score']:.2f}")
            
            # 3. 计算目标仓位
            self.calculate_all_positions(date)
            
            logger.info(f"{date} 的每日计算完成")
            return True
            
        except Exception as e:
            logger.error(f"每日计算失败: {str(e)}")
            return False
