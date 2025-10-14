import React from 'react';
import { RefreshCw, TrendingUp, Database, Star } from 'lucide-react';

const Header = ({ systemStatus, onRefresh, refreshing, onShowIndexSelector }) => {
  return (
    <header className="bg-dark-surface border-b border-dark-border sticky top-0 z-50">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          {/* Logo和标题 */}
          <div className="flex items-center space-x-3">
            <div className="bg-gradient-to-br from-blue-500 to-purple-600 p-2 rounded-lg">
              <TrendingUp className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-dark-text">股债仓位决策系统</h1>
              <p className="text-xs text-dark-muted">智能投资组合管理</p>
            </div>
          </div>

          {/* 状态和操作 */}
          <div className="flex items-center space-x-4">
            {/* 系统状态 */}
            <div className="hidden md:flex items-center space-x-4 text-sm">
              <div className="flex items-center space-x-2">
                <Database className="w-4 h-4 text-dark-muted" />
                <span className="text-dark-muted">
                  总指数: <span className="text-dark-text font-medium">{systemStatus?.total_indices || 0}</span>
                </span>
              </div>
              <div className="flex items-center space-x-2">
                <Star className="w-4 h-4 text-yellow-500" />
                <span className="text-dark-muted">
                  自选: <span className="text-dark-text font-medium">{systemStatus?.favorite_indices || 0}</span>
                </span>
              </div>
              {systemStatus?.latest_data_date && (
                <div className="text-dark-muted">
                  数据日期: <span className="text-dark-text">{systemStatus.latest_data_date}</span>
                </div>
              )}
            </div>

            {/* 操作按钮 */}
            <button
              onClick={onShowIndexSelector}
              className="hidden md:flex items-center space-x-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors"
            >
              <Star className="w-4 h-4" />
              <span>管理自选</span>
            </button>

            <button
              onClick={onRefresh}
              disabled={refreshing}
              className="hidden md:flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
              <span>{refreshing ? '刷新中...' : '刷新数据'}</span>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
