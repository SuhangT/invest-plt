from flask import Flask, jsonify, request
from flask_cors import CORS
from models import db, Index, IndexHistory, CalculatedMetrics, StockBondRatio, SystemConfig
from data_fetcher import DataFetcher
from calculator import Calculator
from scheduler import init_scheduler
from datetime import datetime, timedelta
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# 配置
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "invest.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化数据库
db.init_app(app)

# 初始化工具类
fetcher = DataFetcher()
calculator = Calculator()


@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})


@app.route('/api/indices', methods=['GET'])
def get_indices():
    """获取所有指数列表"""
    try:
        is_favorite = request.args.get('is_favorite')
        search = request.args.get('search', '')
        
        query = Index.query
        
        if is_favorite is not None:
            is_fav = is_favorite.lower() == 'true'
            query = query.filter_by(is_favorite=is_fav)
        
        if search:
            query = query.filter(
                (Index.name.contains(search)) | (Index.code.contains(search))
            )
        
        indices = query.order_by(Index.code).all()
        
        result = []
        for index in indices:
            # 获取最新估值数据
            latest_history = IndexHistory.query.filter_by(
                index_id=index.id
            ).order_by(IndexHistory.date.desc()).first()
            
            # 获取最新计算指标
            latest_metrics = CalculatedMetrics.query.filter_by(
                index_id=index.id
            ).order_by(CalculatedMetrics.date.desc()).first()
            
            data = index.to_dict()
            
            if latest_history:
                data['latest_date'] = latest_history.date.strftime('%Y-%m-%d')
                data['pe_ttm'] = latest_history.pe_ttm
                data['pb'] = latest_history.pb
                data['close'] = latest_history.close
            
            if latest_metrics:
                data['metrics'] = latest_metrics.to_dict()
            
            result.append(data)
        
        return jsonify({
            'success': True,
            'data': result,
            'total': len(result)
        })
        
    except Exception as e:
        logger.error(f"获取指数列表失败: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/indices/<int:index_id>', methods=['GET'])
def get_index_detail(index_id):
    """获取指数详情"""
    try:
        index = Index.query.get(index_id)
        if not index:
            return jsonify({'success': False, 'error': '指数不存在'}), 404
        
        # 获取历史数据
        days = int(request.args.get('days', 365))
        start_date = datetime.now().date() - timedelta(days=days)
        
        history = IndexHistory.query.filter(
            IndexHistory.index_id == index_id,
            IndexHistory.date >= start_date
        ).order_by(IndexHistory.date.asc()).all()
        
        # 获取计算指标历史
        metrics_history = CalculatedMetrics.query.filter(
            CalculatedMetrics.index_id == index_id,
            CalculatedMetrics.date >= start_date
        ).order_by(CalculatedMetrics.date.asc()).all()
        
        return jsonify({
            'success': True,
            'data': {
                'index': index.to_dict(),
                'history': [h.to_dict() for h in history],
                'metrics': [m.to_dict() for m in metrics_history]
            }
        })
        
    except Exception as e:
        logger.error(f"获取指数详情失败: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/indices/<int:index_id>/favorite', methods=['POST'])
def toggle_favorite(index_id):
    """切换自选状态"""
    try:
        index = Index.query.get(index_id)
        if not index:
            return jsonify({'success': False, 'error': '指数不存在'}), 404
        
        data = request.get_json()
        is_favorite = data.get('is_favorite', not index.is_favorite)
        
        index.is_favorite = is_favorite
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': index.to_dict()
        })
        
    except Exception as e:
        logger.error(f"切换自选状态失败: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/indices/<int:index_id>/weight', methods=['PUT'])
def update_manual_weight(index_id):
    """更新人为权重"""
    try:
        index = Index.query.get(index_id)
        if not index:
            return jsonify({'success': False, 'error': '指数不存在'}), 404
        
        data = request.get_json()
        manual_weight = data.get('manual_weight')
        
        if manual_weight is None or manual_weight < 0:
            return jsonify({'success': False, 'error': '权重必须大于等于0'}), 400
        
        index.manual_weight = manual_weight
        db.session.commit()
        
        # 重新计算指标
        calculator.calculate_index_metrics(index_id)
        calculator.calculate_all_positions()
        
        return jsonify({
            'success': True,
            'data': index.to_dict()
        })
        
    except Exception as e:
        logger.error(f"更新权重失败: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/stock-bond-ratio', methods=['GET'])
def get_stock_bond_ratio():
    """获取股债性价比数据"""
    try:
        days = int(request.args.get('days', 3650))
        start_date = datetime.now().date() - timedelta(days=days)
        
        ratios = StockBondRatio.query.filter(
            StockBondRatio.date >= start_date
        ).order_by(StockBondRatio.date.asc()).all()
        
        # 获取最新数据
        latest = StockBondRatio.query.order_by(
            StockBondRatio.date.desc()
        ).first()
        
        return jsonify({
            'success': True,
            'data': {
                'latest': latest.to_dict() if latest else None,
                'history': [r.to_dict() for r in ratios]
            }
        })
        
    except Exception as e:
        logger.error(f"获取股债性价比失败: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    """获取仪表盘数据"""
    try:
        # 获取最新股债性价比
        latest_ratio = StockBondRatio.query.order_by(
            StockBondRatio.date.desc()
        ).first()
        
        # 获取所有自选指数的最新指标
        favorite_indices = Index.query.filter_by(is_favorite=True).all()
        
        indices_data = []
        for index in favorite_indices:
            latest_metrics = CalculatedMetrics.query.filter_by(
                index_id=index.id
            ).order_by(CalculatedMetrics.date.desc()).first()
            
            latest_history = IndexHistory.query.filter_by(
                index_id=index.id
            ).order_by(IndexHistory.date.desc()).first()
            
            if latest_metrics:
                data = {
                    'index': index.to_dict(),
                    'metrics': latest_metrics.to_dict(),
                    'valuation': {
                        'pe_ttm': latest_history.pe_ttm if latest_history else None,
                        'pb': latest_history.pb if latest_history else None,
                        'close': latest_history.close if latest_history else None
                    }
                }
                indices_data.append(data)
        
        return jsonify({
            'success': True,
            'data': {
                'stock_bond_ratio': latest_ratio.to_dict() if latest_ratio else None,
                'indices': indices_data,
                'update_time': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"获取仪表盘数据失败: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/data/refresh', methods=['POST'])
def refresh_data():
    """手动刷新数据"""
    try:
        data = request.get_json() or {}
        refresh_type = data.get('type', 'all')  # 'all', 'indices', 'financials', 'calculate'
        
        if refresh_type in ['all', 'indices']:
            # 刷新指数数据
            logger.info("开始刷新指数数据...")
            favorite_indices = Index.query.filter_by(is_favorite=True).all()
            
            for index in favorite_indices:
                # 获取最近30天数据
                end_date = datetime.now().strftime('%Y%m%d')
                start_date = (datetime.now() - timedelta(days=3650)).strftime('%Y%m%d')
                
                fetcher.fetch_index_history(index.code, start_date, end_date)
                fetcher.fetch_index_constituents(index.code)
        
        if refresh_type in ['all', 'financials']:
            # 刷新财务数据
            logger.info("开始刷新财务数据...")
            fetcher.fetch_latest_financials()
        
        if refresh_type in ['all', 'calculate']:
            # 重新计算
            logger.info("开始重新计算...")
            calculator.run_daily_calculation()
        
        return jsonify({
            'success': True,
            'message': '数据刷新成功'
        })
        
    except Exception as e:
        logger.error(f"刷新数据失败: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/data/init', methods=['POST'])
def init_data():
    """初始化数据（首次运行）"""
    try:
        # 检查是否已初始化
        config = SystemConfig.query.filter_by(key='data_initialized').first()
        if config and config.value == 'true':
            return jsonify({
                'success': False,
                'error': '数据已初始化，请使用刷新接口'
            }), 400
        
        logger.info("开始初始化数据...")
        
        # 1. 获取所有指数列表
        logger.info("1. 获取指数列表...")
        fetcher.fetch_all_indices()
        
        # 2. 获取国债收益率
        logger.info("2. 获取国债收益率...")
        start_date = (datetime.now() - timedelta(days=3650)).strftime('%Y%m%d')
        fetcher.fetch_bond_yield(start_date)
        
        # 3. 获取中证800历史数据（用于股债性价比计算）
        logger.info("3. 获取中证800历史数据...")
        fetcher.fetch_index_history('000906', start_date)
        
        # 4. 获取财务数据
        logger.info("4. 获取财务数据...")
        fetcher.fetch_latest_financials()
        
        # 5. 计算近10年历史股债性价比
        logger.info("5. 计算近10年历史股债性价比...")
        calculator.calculate_historical_stock_bond_ratio()
        
        # 标记为已初始化
        if not config:
            config = SystemConfig(
                key='data_initialized',
                value='true',
                description='数据是否已初始化'
            )
            db.session.add(config)
        else:
            config.value = 'true'
        
        db.session.commit()
        
        logger.info("数据初始化完成")
        
        return jsonify({
            'success': True,
            'message': '数据初始化成功'
        })
        
    except Exception as e:
        logger.error(f"初始化数据失败: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/system/status', methods=['GET'])
def get_system_status():
    """获取系统状态"""
    try:
        # 检查是否已初始化
        config = SystemConfig.query.filter_by(key='data_initialized').first()
        is_initialized = config and config.value == 'true'
        
        # 统计数据
        total_indices = Index.query.count()
        favorite_indices = Index.query.filter_by(is_favorite=True).count()
        
        # 最新数据日期
        latest_history = IndexHistory.query.order_by(
            IndexHistory.date.desc()
        ).first()
        
        latest_ratio = StockBondRatio.query.order_by(
            StockBondRatio.date.desc()
        ).first()
        
        return jsonify({
            'success': True,
            'data': {
                'is_initialized': is_initialized,
                'total_indices': total_indices,
                'favorite_indices': favorite_indices,
                'latest_data_date': latest_history.date.strftime('%Y-%m-%d') if latest_history else None,
                'latest_ratio_date': latest_ratio.date.strftime('%Y-%m-%d') if latest_ratio else None
            }
        })
        
    except Exception as e:
        logger.error(f"获取系统状态失败: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    with app.app_context():
        # 创建数据库表
        db.create_all()
        
        # 初始化定时任务
        init_scheduler(app, calculator, fetcher)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
