import React from 'react';
import { TrendingUp, TrendingDown, DollarSign, PieChart, Wallet } from 'lucide-react';

const Dashboard = ({ data, totalInvestment, onTotalInvestmentChange }) => {

  if (!data || !data.stock_bond_ratio) {
    return (
      <div className="bg-dark-surface rounded-xl p-6 border border-dark-border">
        <div className="text-dark-muted text-center">暂无数据</div>
      </div>
    );
  }

  const ratio = data.stock_bond_ratio;
  const percentile = ratio.percentile_10y || 0;
  const stockAllocation = ratio.stock_allocation || 0;
  const cashAllocation = 100 - stockAllocation;

  // 计算具体金额
  const stockAmount = (totalInvestment * stockAllocation / 100);
  const cashAmount = (totalInvestment * cashAllocation / 100);

  // 根据分位数计算背景色（绿色低估 → 红色高估）
  const getBackgroundColor = (percentile) => {
    if (percentile < 20) return 'from-green-900/30 to-green-800/20';
    if (percentile < 40) return 'from-green-800/20 to-yellow-900/20';
    if (percentile < 60) return 'from-yellow-900/20 to-orange-900/20';
    if (percentile < 80) return 'from-orange-900/20 to-red-900/20';
    return 'from-red-900/30 to-red-800/20';
  };

  const getTextColor = (percentile) => {
    if (percentile < 20) return 'text-green-400';
    if (percentile < 40) return 'text-green-300';
    if (percentile < 60) return 'text-yellow-400';
    if (percentile < 80) return 'text-orange-400';
    return 'text-red-400';
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('zh-CN', {
      style: 'currency',
      currency: 'CNY',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  return (
    <div className={`bg-gradient-to-br ${getBackgroundColor(percentile)} rounded-xl p-6 border border-dark-border fade-in`}>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-dark-text flex items-center space-x-2">
          <PieChart className="w-6 h-6" />
          <span>股债配置仪表盘</span>
        </h2>
        <div className="text-sm text-dark-muted">
          更新时间: {new Date(data.update_time).toLocaleString('zh-CN')}
        </div>
      </div>

      {/* 投资总金额输入 */}
      <div className="mb-6 bg-dark-surface/50 backdrop-blur rounded-lg p-4 border border-dark-border/50">
        <div className="flex items-center space-x-4">
          <Wallet className="w-5 h-5 text-blue-400" />
          <label className="text-sm text-dark-muted">预计投资总金额:</label>
          <input
            type="number"
            value={totalInvestment}
            onChange={(e) => onTotalInvestmentChange(Number(e.target.value) || 0)}
            className="flex-1 max-w-xs px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-dark-text focus:outline-none focus:border-blue-500"
            placeholder="请输入投资总金额"
            min="0"
            step="10000"
          />
          <span className="text-dark-text font-medium">{formatCurrency(totalInvestment)}</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {/* 股债性价比 */}
        <div className="bg-dark-surface/50 backdrop-blur rounded-lg p-4 border border-dark-border/50">
          <div className="flex items-center justify-between mb-2">
            <span className="text-dark-muted text-sm">股债性价比</span>
            <TrendingUp className="w-4 h-4 text-blue-400" />
          </div>
          <div className="text-2xl font-bold text-dark-text">
            {(ratio.ratio * 100).toFixed(2)}%
          </div>
          <div className="text-xs text-dark-muted mt-1">
            中证800 PE: {ratio.csi800_pe?.toFixed(2)} | 国债: {ratio.bond_yield_10y?.toFixed(2)}%
          </div>
        </div>

        {/* 分位数 */}
        <div className="bg-dark-surface/50 backdrop-blur rounded-lg p-4 border border-dark-border/50">
          <div className="flex items-center justify-between mb-2">
            <span className="text-dark-muted text-sm">近10年分位数</span>
            <DollarSign className="w-4 h-4 text-purple-400" />
          </div>
          <div className={`text-2xl font-bold ${getTextColor(percentile)}`}>
            {percentile.toFixed(1)}%
          </div>
          <div className="mt-2">
            <div className="w-full bg-dark-border rounded-full h-2">
              <div
                className={`h-2 rounded-full transition-all duration-500 ${
                  percentile < 50 ? 'bg-gradient-to-r from-green-500 to-yellow-500' : 'bg-gradient-to-r from-orange-500 to-red-500'
                }`}
                style={{ width: `${percentile}%` }}
              />
            </div>
          </div>
        </div>

        {/* 股票配置 */}
        <div className="bg-dark-surface/50 backdrop-blur rounded-lg p-4 border border-dark-border/50">
          <div className="flex items-center justify-between mb-2">
            <span className="text-dark-muted text-sm">股票配置</span>
            <TrendingUp className="w-4 h-4 text-trade-green" />
          </div>
          <div className="text-2xl font-bold text-trade-green">
            {stockAllocation.toFixed(1)}%
          </div>
          <div className="text-lg font-semibold text-trade-green mt-1">
            {formatCurrency(stockAmount)}
          </div>
          <div className="text-xs text-dark-muted mt-1">
            建议投入指数基金
          </div>
        </div>

        {/* 现金配置 */}
        <div className="bg-dark-surface/50 backdrop-blur rounded-lg p-4 border border-dark-border/50">
          <div className="flex items-center justify-between mb-2">
            <span className="text-dark-muted text-sm">现金配置</span>
            <TrendingDown className="w-4 h-4 text-blue-400" />
          </div>
          <div className="text-2xl font-bold text-blue-400">
            {cashAllocation.toFixed(1)}%
          </div>
          <div className="text-lg font-semibold text-blue-400 mt-1">
            {formatCurrency(cashAmount)}
          </div>
          <div className="text-xs text-dark-muted mt-1">
            保留现金或债券
          </div>
        </div>
      </div>

      {/* 配置建议 */}
      <div className="mt-6 bg-dark-surface/50 backdrop-blur rounded-lg p-4 border border-dark-border/50">
        <h3 className="text-sm font-semibold text-dark-text mb-2">配置建议</h3>
        <p className="text-sm text-dark-muted">
          {percentile < 20 && '当前股债性价比处于历史低位，股票相对债券具有较高吸引力，建议增加股票配置。'}
          {percentile >= 20 && percentile < 40 && '当前股债性价比处于较低水平，股票仍有一定吸引力，可适度配置。'}
          {percentile >= 40 && percentile < 60 && '当前股债性价比处于中等水平，建议保持均衡配置。'}
          {percentile >= 60 && percentile < 80 && '当前股债性价比处于较高水平，股票吸引力下降，建议降低股票配置。'}
          {percentile >= 80 && '当前股债性价比处于历史高位，股票相对债券吸引力较低，建议谨慎配置或减仓。'}
        </p>
      </div>
    </div>
  );
};

export default Dashboard;
