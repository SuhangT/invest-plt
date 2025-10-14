import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Dashboard from './components/Dashboard';
import IndexTable from './components/IndexTable';
import IndexSelector from './components/IndexSelector';
import Header from './components/Header';
import InitialSetup from './components/InitialSetup';
import { RefreshCw } from 'lucide-react';

const API_BASE_URL = 'http://localhost:5000/api';

function App() {
  const [systemStatus, setSystemStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [dashboardData, setDashboardData] = useState(null);
  const [showIndexSelector, setShowIndexSelector] = useState(false);

  useEffect(() => {
    checkSystemStatus();
  }, []);

  useEffect(() => {
    if (systemStatus?.is_initialized) {
      loadDashboardData();
      // 每30秒刷新一次数据
      const interval = setInterval(loadDashboardData, 30000);
      return () => clearInterval(interval);
    }
  }, [systemStatus]);

  const checkSystemStatus = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/system/status`);
      if (response.data.success) {
        setSystemStatus(response.data.data);
      }
    } catch (error) {
      console.error('获取系统状态失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadDashboardData = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/dashboard`);
      if (response.data.success) {
        setDashboardData(response.data.data);
      }
    } catch (error) {
      console.error('获取仪表盘数据失败:', error);
    }
  };

  const handleRefreshData = async () => {
    setRefreshing(true);
    try {
      await axios.post(`${API_BASE_URL}/data/refresh`, {
        type: 'all'
      });
      await loadDashboardData();
      await checkSystemStatus();
    } catch (error) {
      console.error('刷新数据失败:', error);
      alert('刷新数据失败: ' + error.message);
    } finally {
      setRefreshing(false);
    }
  };

  const handleInitComplete = () => {
    checkSystemStatus();
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-dark-bg flex items-center justify-center">
        <div className="text-dark-text text-xl">加载中...</div>
      </div>
    );
  }

  if (!systemStatus?.is_initialized) {
    return <InitialSetup onComplete={handleInitComplete} />;
  }

  return (
    <div className="min-h-screen bg-dark-bg">
      <Header 
        systemStatus={systemStatus}
        onRefresh={handleRefreshData}
        refreshing={refreshing}
        onShowIndexSelector={() => setShowIndexSelector(true)}
      />

      <main className="container mx-auto px-4 py-6 space-y-6">
        {/* 仪表盘 */}
        <Dashboard data={dashboardData} />

        {/* 指数表格 */}
        <IndexTable 
          data={dashboardData?.indices || []}
          onDataChange={loadDashboardData}
        />
      </main>

      {/* 指数选择器弹窗 */}
      {showIndexSelector && (
        <IndexSelector
          onClose={() => setShowIndexSelector(false)}
          onUpdate={loadDashboardData}
        />
      )}

      {/* 刷新按钮（移动端） */}
      <button
        onClick={handleRefreshData}
        disabled={refreshing}
        className="fixed bottom-6 right-6 md:hidden bg-blue-600 hover:bg-blue-700 text-white p-4 rounded-full shadow-lg transition-all disabled:opacity-50"
      >
        <RefreshCw className={`w-6 h-6 ${refreshing ? 'animate-spin' : ''}`} />
      </button>
    </div>
  );
}

export default App;
