import React, { useState } from 'react';
import axios from 'axios';
import { ArrowUp, ArrowDown, Edit2, Save, X, TrendingUp, TrendingDown } from 'lucide-react';

const API_BASE_URL = 'http://localhost:5000/api';

const IndexTable = ({ data, onDataChange }) => {
  const [editingWeight, setEditingWeight] = useState(null);
  const [weightValue, setWeightValue] = useState('');

  if (!data || data.length === 0) {
    return (
      <div className="bg-dark-surface rounded-xl p-6 border border-dark-border">
        <div className="text-center text-dark-muted">
          <p className="mb-2">暂无自选指数</p>
          <p className="text-sm">请点击"管理自选"添加指数</p>
        </div>
      </div>
    );
  }

  const getPercentileColor = (range) => {
    if (!range) return 'bg-dark-surface';
    const min = parseInt(range.split('-')[0].replace('%', ''));
    if (min < 10) return 'bg-green-900/40 border-green-700/50';
    if (min < 20) return 'bg-green-800/30 border-green-600/50';
    if (min < 35) return 'bg-yellow-900/30 border-yellow-700/50';
    if (min < 50) return 'bg-yellow-800/30 border-yellow-600/50';
    if (min < 65) return 'bg-orange-900/30 border-orange-700/50';
    if (min < 80) return 'bg-orange-800/30 border-orange-600/50';
    if (min < 90) return 'bg-red-900/30 border-red-700/50';
    return 'bg-red-800/40 border-red-600/50';
  };

  const getOperationBgColor = (signal) => {
    if (signal === 'add') return 'bg-trade-green-light/10 hover:bg-trade-green-light/20';
    if (signal === 'reduce') return 'bg-trade-red-light/10 hover:bg-trade-red-light/20';
    return 'hover:bg-dark-surface/50';
  };

  const handleEditWeight = (indexData) => {
    setEditingWeight(indexData.index.id);
    setWeightValue(indexData.index.manual_weight.toString());
  };

  const handleSaveWeight = async (indexId) => {
    try {
      const weight = parseFloat(weightValue);
      if (isNaN(weight) || weight < 0) {
        alert('请输入有效的权重值（≥0）');
        return;
      }

      await axios.put(`${API_BASE_URL}/indices/${indexId}/weight`, {
        manual_weight: weight
      });

      setEditingWeight(null);
      onDataChange();
    } catch (error) {
      console.error('更新权重失败:', error);
      alert('更新权重失败: ' + error.message);
    }
  };

  const handleCancelEdit = () => {
    setEditingWeight(null);
    setWeightValue('');
  };

  return (
    <div className="bg-dark-surface rounded-xl border border-dark-border overflow-hidden fade-in">
      <div className="p-6 border-b border-dark-border">
        <h2 className="text-xl font-bold text-dark-text">自选指数详情</h2>
        <p className="text-sm text-dark-muted mt-1">根据估值分位和ROE权重计算目标仓位</p>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-dark-bg border-b border-dark-border">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-semibold text-dark-muted uppercase tracking-wider">
                指数名称
              </th>
              <th className="px-4 py-3 text-right text-xs font-semibold text-dark-muted uppercase tracking-wider">
                PE/PB
              </th>
              <th className="px-4 py-3 text-right text-xs font-semibold text-dark-muted uppercase tracking-wider">
                ROE
              </th>
              <th className="px-4 py-3 text-center text-xs font-semibold text-dark-muted uppercase tracking-wider">
                分位区间
              </th>
              <th className="px-4 py-3 text-right text-xs font-semibold text-dark-muted uppercase tracking-wider">
                综合分数
              </th>
              <th className="px-4 py-3 text-right text-xs font-semibold text-dark-muted uppercase tracking-wider">
                人为权重
              </th>
              <th className="px-4 py-3 text-right text-xs font-semibold text-dark-muted uppercase tracking-wider">
                目标仓位
              </th>
              <th className="px-4 py-3 text-center text-xs font-semibold text-dark-muted uppercase tracking-wider">
                操作提示
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-dark-border">
            {data.map((item) => {
              const metrics = item.metrics || {};
              const valuation = item.valuation || {};
              const isEditing = editingWeight === item.index.id;

              return (
                <tr
                  key={item.index.id}
                  className={`transition-colors ${getOperationBgColor(metrics.operation_signal)}`}
                >
                  {/* 指数名称 */}
                  <td className="px-4 py-4">
                    <div>
                      <div className="font-medium text-dark-text">{item.index.name}</div>
                      <div className="text-xs text-dark-muted">{item.index.code}</div>
                    </div>
                  </td>

                  {/* PE/PB */}
                  <td className="px-4 py-4 text-right">
                    <div className="text-sm">
                      <div className="text-dark-text">
                        PE: {valuation.pe_ttm ? valuation.pe_ttm.toFixed(2) : '-'}
                      </div>
                      <div className="text-dark-muted text-xs">
                        PB: {valuation.pb ? valuation.pb.toFixed(2) : '-'}
                      </div>
                    </div>
                  </td>

                  {/* ROE */}
                  <td className="px-4 py-4 text-right">
                    <div className="text-sm">
                      <div className="text-dark-text">
                        {metrics.weighted_roe ? `${metrics.weighted_roe.toFixed(2)}%` : '-'}
                      </div>
                      <div className="text-dark-muted text-xs">
                        权重: {metrics.roe_weight ? metrics.roe_weight.toFixed(2) : '-'}
                      </div>
                    </div>
                  </td>

                  {/* 分位区间 */}
                  <td className="px-4 py-4">
                    <div className="flex justify-center">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getPercentileColor(metrics.percentile_range)}`}>
                        {metrics.percentile_range || '-'}
                      </span>
                    </div>
                  </td>

                  {/* 综合分数 */}
                  <td className="px-4 py-4 text-right">
                    <div className="text-sm">
                      <div className="text-dark-text font-semibold">
                        {metrics.composite_score ? metrics.composite_score.toFixed(2) : '-'}
                      </div>
                      <div className="text-dark-muted text-xs">
                        初始: {metrics.initial_score || '-'}
                      </div>
                    </div>
                  </td>

                  {/* 人为权重 */}
                  <td className="px-4 py-4 text-right">
                    {isEditing ? (
                      <div className="flex items-center justify-end space-x-2">
                        <input
                          type="number"
                          step="0.1"
                          min="0"
                          value={weightValue}
                          onChange={(e) => setWeightValue(e.target.value)}
                          className="w-20 px-2 py-1 bg-dark-bg border border-dark-border rounded text-dark-text text-sm focus:outline-none focus:border-blue-500"
                          autoFocus
                        />
                        <button
                          onClick={() => handleSaveWeight(item.index.id)}
                          className="p-1 text-trade-green hover:bg-trade-green/20 rounded"
                        >
                          <Save className="w-4 h-4" />
                        </button>
                        <button
                          onClick={handleCancelEdit}
                          className="p-1 text-trade-red hover:bg-trade-red/20 rounded"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>
                    ) : (
                      <div className="flex items-center justify-end space-x-2">
                        <span className="text-dark-text">
                          {item.index.manual_weight.toFixed(2)}
                        </span>
                        <button
                          onClick={() => handleEditWeight(item)}
                          className="p-1 text-dark-muted hover:text-blue-400 hover:bg-blue-500/20 rounded"
                        >
                          <Edit2 className="w-4 h-4" />
                        </button>
                      </div>
                    )}
                  </td>

                  {/* 目标仓位 */}
                  <td className="px-4 py-4 text-right">
                    <div className="text-lg font-bold text-blue-400">
                      {metrics.target_position ? `${metrics.target_position.toFixed(2)}%` : '-'}
                    </div>
                  </td>

                  {/* 操作提示 */}
                  <td className="px-4 py-4">
                    {metrics.operation_signal ? (
                      <div className="flex items-center justify-center space-x-2">
                        {metrics.operation_signal === 'add' ? (
                          <>
                            <TrendingDown className="w-5 h-5 text-trade-green" />
                            <div className="text-center">
                              <div className="text-sm font-semibold text-trade-green">
                                建议加仓
                              </div>
                              <div className="text-xs text-dark-muted">
                                {metrics.operation_percent?.toFixed(1)}%
                              </div>
                            </div>
                          </>
                        ) : (
                          <>
                            <TrendingUp className="w-5 h-5 text-trade-red" />
                            <div className="text-center">
                              <div className="text-sm font-semibold text-trade-red">
                                建议减仓
                              </div>
                              <div className="text-xs text-dark-muted">
                                {metrics.operation_percent?.toFixed(1)}%
                              </div>
                            </div>
                          </>
                        )}
                      </div>
                    ) : (
                      <div className="text-center text-dark-muted text-sm">持有</div>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default IndexTable;
