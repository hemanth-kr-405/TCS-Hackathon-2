import React from 'react';
import { Activity, Database, RefreshCw, ShieldCheck, Tv } from 'lucide-react';

interface HeaderProps {
  activeTabTitle: string;
  onRefresh?: () => void;
  isRefreshing?: boolean;
  isPresentationMode: boolean;
  setIsPresentationMode: (val: boolean) => void;
}

export const Header: React.FC<HeaderProps> = ({
  activeTabTitle,
  onRefresh,
  isRefreshing,
  isPresentationMode,
  setIsPresentationMode,
}) => {
  return (
    <header className="bg-white border-b border-[#E2E8F0] px-6 py-3.5 flex flex-col md:flex-row md:items-center justify-between gap-4 sticky top-0 z-10 shadow-xs text-[#18324A]">
      {/* Platform Title & Subtitle */}
      <div className="flex items-center gap-4">
        <div>
          <h2 className="text-base font-heading font-bold tracking-tight text-[#18324A] flex items-center gap-2">
            TCS Retail AI Platform
            <span className="text-[10px] px-2 py-0.5 rounded-full bg-[#DCECF8] text-[#18324A] font-semibold border border-[#A7C7E7]/50">
              Enterprise AI Core
            </span>
          </h2>
          <p className="text-[11px] text-[#64748B] font-medium">
            Conversational AI + Sentiment Intelligence + Business Intelligence
          </p>
        </div>

        <span className="hidden xl:flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-[#E4F5EF] text-[#065F46] border border-[#B8E0D2]">
          <Activity className="w-3.5 h-3.5 text-[#10B981] animate-pulse" />
          Live AI Pipeline Active
        </span>
      </div>

      {/* Control Actions & Presentation Mode Toggle */}
      <div className="flex items-center gap-3">
        {/* Presentation Mode Toggle Switch */}
        <button
          onClick={() => setIsPresentationMode(!isPresentationMode)}
          className={`flex items-center gap-2 px-3.5 py-1.5 rounded-xl text-xs font-semibold transition border ${
            isPresentationMode
              ? 'bg-[#18324A] text-white border-[#18324A] shadow-sm'
              : 'bg-[#F8FAFC] text-[#18324A] hover:bg-[#F1F5F9] border-[#E2E8F0]'
          }`}
          title="Toggle Hackathon Presentation Mode"
        >
          <Tv className={`w-3.5 h-3.5 ${isPresentationMode ? 'text-[#B8E0D2]' : 'text-[#64748B]'}`} />
          {isPresentationMode ? 'Presentation Mode ON' : 'Presentation Mode OFF'}
        </button>

        <div className="hidden lg:flex items-center gap-3 text-xs bg-[#F8FAFC] px-3 py-1.5 rounded-xl border border-[#E2E8F0]">
          <span className="flex items-center gap-1.5 text-[#18324A] font-medium">
            <Database className="w-3.5 h-3.5 text-[#0284C7]" />
            Dataset: <strong className="text-[#0284C7]">23.4k Reviews</strong>
          </span>
          <span className="text-[#CBD5E1]">|</span>
          <span className="flex items-center gap-1.5 text-[#18324A] font-medium">
            <ShieldCheck className="w-3.5 h-3.5 text-[#10B981]" />
            Eval: <strong className="text-[#10B981]">86.4% Accuracy</strong>
          </span>
        </div>

        {onRefresh && (
          <button
            onClick={onRefresh}
            disabled={isRefreshing}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold bg-[#DCECF8] hover:bg-[#A7C7E7]/40 text-[#18324A] rounded-xl transition border border-[#A7C7E7]/60 shadow-xs disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        )}
      </div>
    </header>
  );
};
