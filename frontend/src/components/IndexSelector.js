import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { X, Search, Star, StarOff, Loader } from 'lucide-react';

const API_BASE_URL = 'http://localhost:5000/api';

const IndexSelector = ({ onClose, onUpdate }) => {
  const [indices, setIndices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filter, setFilter] = useState('all'); // 'all', 'favorite', 'non-favorite'

  useEffect(() => {
    loadIndices();
  }, []);

  const loadIndices = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/indices`);
      if (response.data.success) {
        setIndices(response.data.data);
      }
    } catch (error) {
      console.error('获取指数列表失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleFavorite = async (indexId, currentStatus) => {
    try {
      await axios.post(`${API_BASE_URL}/indices/${indexId}/favorite`, {
        is_favorite: !currentStatus
      });
      
      // 更新本地状态
      setIndices(indices.map(idx => 
        idx.id === indexId ? { ...idx, is_favorite: !currentStatus } : idx
      ));
      
      onUpdate();
    } catch (error) {
      console.error('切换自选状态失败:', error);
      alert('操作失败: ' + error.message);
    }
  };

  const filteredIndices = indices.filter(idx => {
    const matchesSearch = 
      idx.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      idx.code.includes(searchTerm);
    
    const matchesFilter = 
      filter === 'all' ||
      (filter === 'favorite' && idx.is_favorite) ||
      (filter === 'non-favorite' && !idx.is_favorite);
    
    return matchesSearch && matchesFilter;
  });

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-dark-surface rounded-xl border border-dark-border w-full max-w-4xl max-h-[90vh] flex flex-col">
        {/* 头部 */}
        <div className="flex items-center justify-between p-6 border-b border-dark-border">
          <h2 className="text-2xl font-bold text-dark-text">管理自选指数</h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-dark-bg rounded-lg transition-colors"
          >
            <X className="w-6 h-6 text-dark-muted" />
          </button>
        </div>

        {/* 搜索和筛选 */}
        <div className="p-6 border-b border-dark-border space-y-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-dark-muted" />
            <input
              type="text"
              placeholder="搜索指数名称或代码..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-3 bg-dark-bg border border-dark-border rounded-lg text-dark-text placeholder-dark-muted focus:outline-none focus:border-blue-500"
            />
          </div>

          <div className="flex space-x-2">
            <button
              onClick={() => setFilter('all')}
              className={`px-4 py-2 rounded-lg transition-colors ${
                filter === 'all'
                  ? 'bg-blue-600 text-white'
                  : 'bg-dark-bg text-dark-muted hover:bg-dark-border'
              }`}
            >
              全部 ({indices.length})
            </button>
            <button
              onClick={() => setFilter('favorite')}
              className={`px-4 py-2 rounded-lg transition-colors ${
                filter === 'favorite'
                  ? 'bg-blue-600 text-white'
                  : 'bg-dark-bg text-dark-muted hover:bg-dark-border'
              }`}
            >
              已自选 ({indices.filter(i => i.is_favorite).length})
            </button>
            <button
              onClick={() => setFilter('non-favorite')}
              className={`px-4 py-2 rounded-lg transition-colors ${
                filter === 'non-favorite'
                  ? 'bg-blue-600 text-white'
                  : 'bg-dark-bg text-dark-muted hover:bg-dark-border'
              }`}
            >
              未自选 ({indices.filter(i => !i.is_favorite).length})
            </button>
          </div>
        </div>

        {/* 指数列表 */}
        <div className="flex-1 overflow-y-auto p-6">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader className="w-8 h-8 text-blue-500 animate-spin" />
            </div>
          ) : filteredIndices.length === 0 ? (
            <div className="text-center py-12 text-dark-muted">
              <p>未找到匹配的指数</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {filteredIndices.map((index) => (
                <div
                  key={index.id}
                  className="bg-dark-bg border border-dark-border rounded-lg p-4 hover:border-blue-500/50 transition-colors"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <h3 className="font-semibold text-dark-text truncate">
                        {index.name}
                      </h3>
                      <p className="text-sm text-dark-muted mt-1">{index.code}</p>
                      
                      {index.latest_date && (
                        <div className="mt-2 text-xs text-dark-muted space-y-1">
                          <div>最新日期: {index.latest_date}</div>
                          {index.pe_ttm && (
                            <div className="flex space-x-4">
                              <span>PE: {index.pe_ttm.toFixed(2)}</span>
                              {index.pb && <span>PB: {index.pb.toFixed(2)}</span>}
                            </div>
                          )}
                        </div>
                      )}
                    </div>

                    <button
                      onClick={() => handleToggleFavorite(index.id, index.is_favorite)}
                      className={`ml-4 p-2 rounded-lg transition-colors ${
                        index.is_favorite
                          ? 'bg-yellow-500/20 text-yellow-500 hover:bg-yellow-500/30'
                          : 'bg-dark-border text-dark-muted hover:bg-dark-border/70'
                      }`}
                    >
                      {index.is_favorite ? (
                        <Star className="w-5 h-5 fill-current" />
                      ) : (
                        <StarOff className="w-5 h-5" />
                      )}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* 底部 */}
        <div className="p-6 border-t border-dark-border flex justify-between items-center">
          <div className="text-sm text-dark-muted">
            已选择 {indices.filter(i => i.is_favorite).length} 个指数
          </div>
          <button
            onClick={onClose}
            className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
          >
            完成
          </button>
        </div>
      </div>
    </div>
  );
};

export default IndexSelector;
