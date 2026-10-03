import React, { useState, useEffect } from 'react';
import type { ViewTab } from './types';
import { Sidebar } from './components/layout/Sidebar';
import { Header } from './components/layout/Header';
import { DashboardView } from './components/views/DashboardView';
import { ChatbotView } from './components/views/ChatbotView';
import { AIOperationsView } from './components/views/AIOperationsView';
import { DatasetExplorerView } from './components/views/DatasetExplorerView';
import { FeedbackView } from './components/views/FeedbackView';
import { SentimentView } from './components/views/SentimentView';
import { IntentView } from './components/views/IntentView';
import { RecurringIssuesView } from './components/views/RecurringIssuesView';
import { EscalationsView } from './components/views/EscalationsView';
import { RecommendationsView } from './components/views/RecommendationsView';
import { HistoryView } from './components/views/HistoryView';
import { ModelEvalView } from './components/views/ModelEvalView';
import { SettingsView } from './components/views/SettingsView';

import { analyticsApi, escalationsApi } from './services/api';
import { AnalyticsOverview, EscalationItem } from './types';

export function App() {
  const [activeTab, setActiveTab] = useState<ViewTab>('dashboard');
  const [analyticsData, setAnalyticsData] = useState<AnalyticsOverview | null>(null);
  const [escalations, setEscalations] = useState<EscalationItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [isPresentationMode, setIsPresentationMode] = useState<boolean>(false);

  const loadData = async () => {
    setLoading(true);
    try {
      const overview = await analyticsApi.getOverview();
      setAnalyticsData(overview);

      const escList = await escalationsApi.list();
      setEscalations(escList);
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const renderActiveView = () => {
    switch (activeTab) {
      case 'dashboard':
        return <DashboardView data={analyticsData} onNavigate={(tab: ViewTab) => setActiveTab(tab)} />;
      case 'chatbot':
        return <ChatbotView isPresentationMode={isPresentationMode} />;
      case 'aiops':
        return <AIOperationsView />;
      case 'dataset':
        return <DatasetExplorerView />;
      case 'feedback':
        return <FeedbackView />;
      case 'analytics':
        return <SentimentView data={analyticsData} />;
      case 'intent':
        return <IntentView data={analyticsData} />;
      case 'issues':
        return <RecurringIssuesView issues={analyticsData?.top_recurring_issues || []} />;
      case 'escalations':
        return <EscalationsView escalations={escalations} onRefresh={loadData} />;
      case 'recommendations':
        return <RecommendationsView recommendations={analyticsData?.recommendations || []} />;
      case 'history':
        return <HistoryView />;
      case 'modeleval':
        return <ModelEvalView />;
      case 'settings':
        return <SettingsView />;
      default:
        return <DashboardView data={analyticsData} onNavigate={(tab: ViewTab) => setActiveTab(tab)} />;
    }
  };

  return (
    <div className="flex min-h-screen bg-[#F5F5F5] font-sans antialiased text-[#18324A]">
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        activeEscalationsCount={escalations.filter((e) => e.status === 'Pending').length}
      />
      <div className="flex-1 flex flex-col min-w-0">
        <Header
          activeTabTitle={activeTab}
          onRefresh={loadData}
          isRefreshing={loading}
          isPresentationMode={isPresentationMode}
          setIsPresentationMode={setIsPresentationMode}
        />
        <main className="flex-1 overflow-y-auto">{renderActiveView()}</main>
      </div>
    </div>
  );
}

export default App;
