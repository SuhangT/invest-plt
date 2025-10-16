import React, { useState, useRef, useEffect } from 'react';
import { RefreshCw, TrendingUp, Database, Star, ChevronDown } from 'lucide-react';

const Header = ({ systemStatus, onRefresh, refreshing, onShowIndexSelector }) => {
  const [showRefreshMenu, setShowRefreshMenu] = useState(false);
  const menuRef = useRef(null);

  // 点击外部关闭菜单
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setShowRefreshMenu(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleRefreshClick = (type) => {
    setShowRefreshMenu(false);
    onRefresh(type);
  };

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

            {/* 刷新数据下拉菜单 */}
            <div className="hidden md:block relative" ref={menuRef}>
              <button
                onClick={() => setShowRefreshMenu(!showRefreshMenu)}
                disabled={refreshing}
                className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors disabled:opacity-50"
              >
                <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
                <span>{refreshing ? '刷新中...' : '刷新数据'}</span>
                <ChevronDown className="w-4 h-4" />
              </button>

              {showRefreshMenu && !refreshing && (
                <div className="absolute right-0 mt-2 w-48 bg-dark-surface border border-dark-border rounded-lg shadow-xl overflow-hidden z-50">
                  <button
                    onClick={() => handleRefreshClick('all')}
                    className="w-full px-4 py-3 text-left text-dark-text hover:bg-dark-bg transition-colors flex items-center space-x-2"
                  >
                    <RefreshCw className="w-4 h-4" />
                    <span>全部刷新</span>
                  </button>
                  <button
                    onClick={() => handleRefreshClick('indices')}
                    className="w-full px-4 py-3 text-left text-dark-text hover:bg-dark-bg transition-colors flex items-center space-x-2 border-t border-dark-border"
                  >
                    <Database className="w-4 h-4" />
                    <span>指数数据</span>
                  </button>
                  <button
                    onClick={() => handleRefreshClick('financials')}
                    className="w-full px-4 py-3 text-left text-dark-text hover:bg-dark-bg transition-colors flex items-center space-x-2 border-t border-dark-border"
                  >
                    <TrendingUp className="w-4 h-4" />
                    <span>财务数据</span>
                  </button>
                  <button
                    onClick={() => handleRefreshClick('calculate')}
                    className="w-full px-4 py-3 text-left text-dark-text hover:bg-dark-bg transition-colors flex items-center space-x-2 border-t border-dark-border"
                  >
                    <Star className="w-4 h-4" />
                    <span>重新计算</span>
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
