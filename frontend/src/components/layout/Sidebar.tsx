import React from 'react';
import type { ViewTab } from '../../types';
import {
  LayoutDashboard,
  Bot,
  MessageSquarePlus,
  BarChart3,
  Target,
  AlertTriangle,
  Flame,
  Lightbulb,
  History,
  Cpu,
  Settings,
  BrainCircuit,
  Database,
  Server,
  ChevronRight,
} from 'lucide-react';

interface SidebarProps {
  activeTab: ViewTab;
  setActiveTab: (tab: ViewTab) => void;
  activeEscalationsCount?: number;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  setActiveTab,
  activeEscalationsCount = 0,
}) => {
  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'chatbot', label: 'AI Command Center', icon: Bot, badge: 'Empathetic AI' },
    { id: 'aiops', label: 'AI Operations Center', icon: Server, badge: 'Control Plane' },
    { id: 'dataset', label: 'Dataset Explorer', icon: Database, badge: '23.4k Reviews' },
    { id: 'feedback', label: 'Feedback Analysis', icon: MessageSquarePlus },
    { id: 'analytics', label: 'Sentiment Analytics', icon: BarChart3 },
    { id: 'intent', label: 'Customer Intent', icon: Target },
    { id: 'issues', label: 'Recurring Issues', icon: AlertTriangle },
    { id: 'escalations', label: 'Escalations', icon: Flame, alertCount: activeEscalationsCount },
    { id: 'recommendations', label: 'Recommendations', icon: Lightbulb },
    { id: 'history', label: 'Conversation History', icon: History },
    { id: 'modeleval', label: 'Model Performance', icon: Cpu },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <aside className="w-64 bg-white border-r border-[#E2E8F0] text-[#18324A] flex flex-col h-screen sticky top-0 shadow-sm z-20">
      {/* Brand Header */}
      <div className="p-5 border-b border-[#E2E8F0] flex items-center gap-3 bg-[#F8FAFC]">
        <div className="p-2.5 bg-[#DCECF8] text-[#18324A] rounded-xl border border-[#A7C7E7]/40 shadow-sm">
          <BrainCircuit className="w-5 h-5 text-[#18324A]" />
        </div>
        <div>
          <h1 className="font-heading font-bold text-sm text-[#18324A] tracking-tight">TCS Retail AI</h1>
          <p className="text-[11px] text-[#64748B] font-medium">Enterprise Intelligence</p>
        </div>
      </div>

      {/* Navigation List */}
      <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id as ViewTab)}
              className={`w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-medium transition-all duration-150 ${
                isActive
                  ? 'bg-[#DCECF8] text-[#18324A] font-semibold border border-[#A7C7E7]/60 shadow-sm'
                  : 'text-[#64748B] hover:text-[#18324A] hover:bg-[#F1F5F9]'
              }`}
            >
              <div className="flex items-center gap-2.5">
                <Icon className={`w-4 h-4 ${isActive ? 'text-[#18324A]' : 'text-[#64748B]'}`} />
                <span>{item.label}</span>
              </div>
              
              <div className="flex items-center gap-1.5">
                {item.badge && (
                  <span className="text-[10px] bg-[#E4F5EF] text-[#065F46] px-2 py-0.5 rounded-full font-semibold border border-[#B8E0D2]">
                    {item.badge}
                  </span>
                )}
                {item.alertCount ? item.alertCount > 0 && (
                  <span className="text-[10px] bg-[#FEF2F2] text-[#EF4444] border border-[#F87171]/40 px-2 py-0.5 rounded-full font-bold">
                    {item.alertCount}
                  </span>
                ) : null}
                {isActive && <ChevronRight className="w-3.5 h-3.5 text-[#18324A]" />}
              </div>
            </button>
          );
        })}
      </nav>

      {/* Footer Info */}
      <div className="p-4 border-t border-[#E2E8F0] bg-[#F8FAFC] text-xs text-[#64748B]">
        <div className="flex items-center justify-between font-medium text-[11px]">
          <span>TF-IDF + ML Core</span>
          <span className="flex items-center gap-1 text-[#10B981] font-semibold">
            <span className="w-2 h-2 rounded-full bg-[#10B981] animate-pulse"></span>
            Online
          </span>
        </div>
        <p className="mt-1 text-[10px] text-[#94A3B8]">TCS Hackathon Release v1.0</p>
      </div>
    </aside>
  );
};
