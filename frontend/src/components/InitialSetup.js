import React, { useState } from 'react';
import axios from 'axios';
import { Database, CheckCircle, AlertCircle, Loader } from 'lucide-react';

const API_BASE_URL = 'http://localhost:5000/api';

const InitialSetup = ({ onComplete }) => {
  const [status, setStatus] = useState('idle'); // 'idle', 'initializing', 'success', 'error'
  const [progress, setProgress] = useState('');
  const [error, setError] = useState('');

  const handleInitialize = async () => {
    setStatus('initializing');
    setError('');
    
    try {
      setProgress('正在初始化数据库...');
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setProgress('正在获取指数列表...');
      await axios.post(`${API_BASE_URL}/data/init`);
      
      setProgress('初始化完成！');
      setStatus('success');
      
      setTimeout(() => {
        onComplete();
      }, 2000);
      
    } catch (err) {
      console.error('初始化失败:', err);
      setError(err.response?.data?.error || err.message || '初始化失败');
      setStatus('error');
    }
  };

  return (
    <div className="min-h-screen bg-dark-bg flex items-center justify-center p-4">
      <div className="max-w-2xl w-full">
        <div className="bg-dark-surface rounded-xl border border-dark-border p-8 text-center">
          {/* Logo */}
          <div className="flex justify-center mb-6">
            <div className="bg-gradient-to-br from-blue-500 to-purple-600 p-4 rounded-2xl">
              <Database className="w-12 h-12 text-white" />
            </div>
          </div>

          {/* 标题 */}
          <h1 className="text-3xl font-bold text-dark-text mb-2">
            欢迎使用股债仓位决策系统
          </h1>
          <p className="text-dark-muted mb-8">
            首次使用需要初始化数据，这可能需要5-10分钟
          </p>

          {/* 状态显示 */}
          {status === 'idle' && (
            <div className="space-y-6">
              <div className="bg-dark-bg rounded-lg p-6 text-left space-y-3">
                <h3 className="font-semibold text-dark-text mb-3">初始化将执行以下操作：</h3>
                <div className="space-y-2 text-sm text-dark-muted">
                  <div className="flex items-start space-x-2">
                    <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                    <span>获取所有中证指数列表</span>
                  </div>
                  <div className="flex items-start space-x-2">
                    <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                    <span>获取近10年国债收益率数据</span>
                  </div>
                  <div className="flex items-start space-x-2">
                    <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                    <span>获取中证800历史数据（用于股债性价比计算）</span>
                  </div>
                  <div className="flex items-start space-x-2">
                    <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                    <span>获取最新季度财务数据</span>
                  </div>
                </div>
              </div>

              <div className="bg-yellow-900/20 border border-yellow-700/50 rounded-lg p-4 text-left">
                <div className="flex items-start space-x-2">
                  <AlertCircle className="w-5 h-5 text-yellow-500 flex-shrink-0 mt-0.5" />
                  <div className="text-sm text-yellow-200">
                    <p className="font-semibold mb-1">注意事项：</p>
                    <ul className="list-disc list-inside space-y-1 text-yellow-300/80">
                      <li>初始化过程中请勿关闭浏览器</li>
                      <li>需要稳定的网络连接</li>
                      <li>akshare接口有频率限制，请耐心等待</li>
                    </ul>
                  </div>
                </div>
              </div>

              <button
                onClick={handleInitialize}
                className="w-full px-6 py-4 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold rounded-lg transition-all transform hover:scale-105"
              >
                开始初始化
              </button>
            </div>
          )}

          {status === 'initializing' && (
            <div className="space-y-6">
              <Loader className="w-16 h-16 text-blue-500 animate-spin mx-auto" />
              <div>
                <p className="text-dark-text font-semibold mb-2">正在初始化...</p>
                <p className="text-dark-muted text-sm">{progress}</p>
              </div>
              <div className="bg-dark-bg rounded-lg p-4">
                <div className="w-full bg-dark-border rounded-full h-2">
                  <div className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full animate-pulse-slow" style={{ width: '60%' }} />
                </div>
              </div>
            </div>
          )}

          {status === 'success' && (
            <div className="space-y-6">
              <CheckCircle className="w-16 h-16 text-green-500 mx-auto" />
              <div>
                <p className="text-dark-text font-semibold text-xl mb-2">初始化成功！</p>
                <p className="text-dark-muted">正在跳转到主界面...</p>
              </div>
            </div>
          )}

          {status === 'error' && (
            <div className="space-y-6">
              <AlertCircle className="w-16 h-16 text-red-500 mx-auto" />
              <div>
                <p className="text-dark-text font-semibold text-xl mb-2">初始化失败</p>
                <p className="text-red-400 text-sm mb-4">{error}</p>
                <button
                  onClick={handleInitialize}
                  className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
                >
                  重试
                </button>
              </div>
            </div>
          )}
        </div>

        {/* 底部说明 */}
        <div className="mt-6 text-center text-sm text-dark-muted">
          <p>初始化完成后，您可以添加自选指数并开始使用决策系统</p>
        </div>
      </div>
    </div>
  );
};

export default InitialSetup;
