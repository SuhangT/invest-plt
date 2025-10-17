from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Index(db.Model):
    """指数基本信息表"""
    __tablename__ = 'indices'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    name_full = db.Column(db.String(200))
    is_favorite = db.Column(db.Boolean, default=False)  # 是否加入自选
    manual_weight = db.Column(db.Float, default=1.0)  # 人为权重
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关联关系
    historical_data = db.relationship('IndexHistory', backref='index', lazy='dynamic', cascade='all, delete-orphan')
    constituents = db.relationship('IndexConstituent', backref='index', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'name_full': self.name_full,
            'is_favorite': self.is_favorite,
            'manual_weight': self.manual_weight
        }


class IndexHistory(db.Model):
    """指数历史数据表"""
    __tablename__ = 'index_history'
    
    id = db.Column(db.Integer, primary_key=True)
    index_id = db.Column(db.Integer, db.ForeignKey('indices.id'), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    open = db.Column(db.Float)
    high = db.Column(db.Float)
    low = db.Column(db.Float)
    close = db.Column(db.Float)
    volume = db.Column(db.Float)  # 成交量（万手）
    amount = db.Column(db.Float)  # 成交金额（亿元）
    pe_ttm = db.Column(db.Float)  # 滚动市盈率
    pb = db.Column(db.Float)  # 市净率
    sample_count = db.Column(db.Integer)  # 样本数量
    
    __table_args__ = (
        db.UniqueConstraint('index_id', 'date', name='uix_index_date'),
    )
    
    def to_dict(self):
        return {
            'date': self.date.strftime('%Y-%m-%d'),
            'open': self.open,
            'high': self.high,
            'low': self.low,
            'close': self.close,
            'volume': self.volume,
            'amount': self.amount,
            'pe_ttm': self.pe_ttm,
            'pb': self.pb,
            'sample_count': self.sample_count
        }


class IndexConstituent(db.Model):
    """指数成份股表"""
    __tablename__ = 'index_constituents'
    
    id = db.Column(db.Integer, primary_key=True)
    index_id = db.Column(db.Integer, db.ForeignKey('indices.id'), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    stock_code = db.Column(db.String(20), nullable=False)
    stock_name = db.Column(db.String(100))
    stock_name_en = db.Column(db.String(200))
    exchange = db.Column(db.String(50))
    weight = db.Column(db.Float)  # 权重（%）
    
    __table_args__ = (
        db.UniqueConstraint('index_id', 'date', 'stock_code', name='uix_index_date_stock'),
    )


class StockFinancial(db.Model):
    """股票财务数据表"""
    __tablename__ = 'stock_financials'
    
    id = db.Column(db.Integer, primary_key=True)
    stock_code = db.Column(db.String(20), nullable=False, index=True)
    stock_name = db.Column(db.String(100))
    report_date = db.Column(db.Date, nullable=False, index=True)  # 报告期
    net_profit = db.Column(db.Float)  # 净利润
    equity = db.Column(db.Float)  # 净资产
    roe = db.Column(db.Float)  # 净资产收益率（%）
    
    __table_args__ = (
        db.UniqueConstraint('stock_code', 'report_date', name='uix_stock_report'),
    )


class BondYield(db.Model):
    """国债收益率表"""
    __tablename__ = 'bond_yields'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, unique=True, nullable=False, index=True)
    yield_10y = db.Column(db.Float)  # 10年国债收益率（%）
    
    def to_dict(self):
        return {
            'date': self.date.strftime('%Y-%m-%d'),
            'yield_10y': self.yield_10y
        }


class CalculatedMetrics(db.Model):
    """计算指标表（每日计算结果）"""
    __tablename__ = 'calculated_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    index_id = db.Column(db.Integer, db.ForeignKey('indices.id'), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    
    # 估值分位数
    pe_percentile = db.Column(db.Float)  # PE分位数
    pb_percentile = db.Column(db.Float)  # PB分位数
    
    # ROE相关
    weighted_roe = db.Column(db.Float)  # 加权ROE
    roe_weight = db.Column(db.Float)  # ROE权重
    
    # 分位区间和分数
    percentile_range = db.Column(db.String(20))  # 如"10%-20%"
    initial_score = db.Column(db.Float)  # 初始分数
    composite_weight = db.Column(db.Float)  # 综合权重 = ROE权重 × 人为权重
    composite_score = db.Column(db.Float)  # 综合分数 = 初始分数 × 综合权重
    
    # 目标仓位
    target_position = db.Column(db.Float)  # 目标仓位（%）
    
    # 操作提示
    operation_signal = db.Column(db.String(20))  # 'add'/'reduce'/null
    operation_percent = db.Column(db.Float)  # 建议加仓/减仓百分比
    previous_range = db.Column(db.String(20))  # 前一日分位区间
    
    __table_args__ = (
        db.UniqueConstraint('index_id', 'date', name='uix_metrics_index_date'),
    )
    
    def to_dict(self):
        return {
            'date': self.date.strftime('%Y-%m-%d'),
            'pe_percentile': self.pe_percentile,
            'pb_percentile': self.pb_percentile,
            'weighted_roe': self.weighted_roe,
            'roe_weight': self.roe_weight,
            'percentile_range': self.percentile_range,
            'initial_score': self.initial_score,
            'composite_weight': self.composite_weight,
            'composite_score': self.composite_score,
            'target_position': self.target_position,
            'operation_signal': self.operation_signal,
            'operation_percent': self.operation_percent,
            'previous_range': self.previous_range
        }


class StockBondRatio(db.Model):
    """股债性价比表"""
    __tablename__ = 'stock_bond_ratios'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, unique=True, nullable=False, index=True)
    csi800_pe = db.Column(db.Float)  # 中证800市盈率
    bond_yield_10y = db.Column(db.Float)  # 10年国债收益率
    ratio = db.Column(db.Float)  # 股债性价比 = 1/PE - 国债收益率
    percentile_10y = db.Column(db.Float)  # 近10年分位数
    stock_allocation = db.Column(db.Float)  # 股票配置比例（%）
    
    def to_dict(self):
        return {
            'date': self.date.strftime('%Y-%m-%d'),
            'csi800_pe': self.csi800_pe,
            'bond_yield_10y': self.bond_yield_10y,
            'ratio': self.ratio,
            'percentile_10y': self.percentile_10y,
            'stock_allocation': self.stock_allocation
        }


class SystemConfig(db.Model):
    """系统配置表"""
    __tablename__ = 'system_config'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.Text)
    description = db.Column(db.String(200))
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
