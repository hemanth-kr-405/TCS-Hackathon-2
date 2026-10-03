import React from 'react';
import type { AnalyticsOverview, ViewTab } from '../../types';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
} from 'recharts';
import {
  MessageSquare,
  TrendingUp,
  Smile,
  ArrowUpRight,
  ShieldAlert,
  Sparkles,
  AlertCircle,
  Building2,
} from 'lucide-react';

interface DashboardViewProps {
  data: AnalyticsOverview | null;
  onNavigate: (tab: ViewTab) => void;
}

const SENTIMENT_COLORS = {
  Positive: '#10B981', // Mint / Emerald
  Neutral: '#0284C7',  // Sky Blue
  Negative: '#EF4444', // Soft Red
};

export const DashboardView: React.FC<DashboardViewProps> = ({ data, onNavigate }) => {
  if (!data) {
    return (
      <div className="p-8 flex items-center justify-center text-[#64748B] text-sm">
        Loading analytics overview...
      </div>
    );
  }

  const pieData = [
    { name: 'Positive', value: data.positive_count },
    { name: 'Neutral', value: data.neutral_count },
    { name: 'Negative', value: data.negative_count },
  ];

  // Department Sentiment Breakdown
  const deptData = [
    { department: 'Dresses', Positive: 420, Neutral: 120, Negative: 80 },
    { department: 'Tops', Positive: 380, Neutral: 150, Negative: 90 },
    { department: 'Bottoms', Positive: 310, Neutral: 95, Negative: 65 },
    { department: 'Outerwear', Positive: 240, Neutral: 70, Negative: 45 },
    { department: 'Shipping', Positive: 95, Neutral: 60, Negative: 180 },
    { department: 'Support', Positive: 110, Neutral: 85, Negative: 140 },
  ];

  return (
    <div className="p-6 space-y-6 bg-[#F5F5F5] min-h-screen text-[#18324A] fade-in">
      {/* Executive Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white border border-[#E2E8F0] p-6 rounded-2xl shadow-xs">
        <div>
          <h2 className="text-xl font-heading font-bold text-[#18324A] flex items-center gap-2">
            Retail Business Intelligence Dashboard
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-[#E4F5EF] text-[#065F46] font-semibold border border-[#B8E0D2]">
              Live Telemetry
            </span>
          </h2>
          <p className="text-xs text-[#64748B] mt-1 font-medium">
            Executive overview: Conversational AI + Sentiment Intelligence + Business Intelligence
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => onNavigate('chatbot')}
            className="px-4 py-2.5 bg-[#18324A] hover:bg-[#0F2232] text-white font-semibold text-xs rounded-xl shadow-xs flex items-center gap-2 transition"
          >
            <Sparkles className="w-4 h-4 text-[#B8E0D2]" />
            AI Command Center
          </button>
        </div>
      </div>

      {/* Overview KPI Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        {/* KPI 1 */}
        <div className="p-5 bg-white border border-[#E2E8F0] rounded-2xl shadow-xs flex items-center justify-between">
          <div>
            <p className="text-xs text-[#64748B] font-medium">Total Feedback Analyzed</p>
            <h3 className="text-2xl font-heading font-bold text-[#18324A] mt-1">{data.total_feedback.toLocaleString()}</h3>
            <span className="text-[11px] text-[#10B981] font-semibold flex items-center gap-1 mt-1">
              <TrendingUp className="w-3.5 h-3.5" /> 23,486 Review Base
            </span>
          </div>
          <div className="p-3 bg-[#DCECF8] text-[#18324A] rounded-xl border border-[#A7C7E7]/40">
            <MessageSquare className="w-5 h-5 text-[#18324A]" />
          </div>
        </div>

        {/* KPI 2 */}
        <div className="p-5 bg-white border border-[#E2E8F0] rounded-2xl shadow-xs flex items-center justify-between">
          <div>
            <p className="text-xs text-[#64748B] font-medium">Avg Sentiment Score</p>
            <h3 className="text-2xl font-heading font-bold text-[#18324A] mt-1">
              {data.average_sentiment_score > 0 ? `+${data.average_sentiment_score}` : data.average_sentiment_score}
            </h3>
            <span className="text-[11px] text-[#0284C7] font-medium mt-1 inline-block">
              Continuous Scale (-1.0 to +1.0)
            </span>
          </div>
          <div className="p-3 bg-[#E4F5EF] text-[#065F46] rounded-xl border border-[#B8E0D2]">
            <Smile className="w-5 h-5 text-[#10B981]" />
          </div>
        </div>

        {/* KPI 3 */}
        <div className="p-5 bg-white border border-[#E2E8F0] rounded-2xl shadow-xs flex items-center justify-between">
          <div>
            <p className="text-xs text-[#64748B] font-medium">CSAT Index</p>
            <h3 className="text-2xl font-heading font-bold text-[#18324A] mt-1">{data.csat_percentage}%</h3>
            <span className="text-[11px] text-[#10B981] font-semibold mt-1 inline-block">
              Positive Customer Satisfaction
            </span>
          </div>
          <div className="p-3 bg-[#E4F5EF] text-[#065F46] rounded-xl border border-[#B8E0D2]">
            <TrendingUp className="w-5 h-5 text-[#10B981]" />
          </div>
        </div>

        {/* KPI 4 */}
        <div className="p-5 bg-white border border-[#E2E8F0] rounded-2xl shadow-xs flex items-center justify-between">
          <div>
            <p className="text-xs text-[#64748B] font-medium">Active Escalations</p>
            <h3 className="text-2xl font-heading font-bold text-[#EF4444] mt-1">{data.active_escalations}</h3>
            <button
              onClick={() => onNavigate('escalations')}
              className="text-[11px] text-[#EF4444] hover:underline font-semibold flex items-center gap-1 mt-1"
            >
              Supervisor Queue <ArrowUpRight className="w-3 h-3" />
            </button>
          </div>
          <div className="p-3 bg-[#FEF2F2] text-[#EF4444] rounded-xl border border-[#F87171]/30">
            <ShieldAlert className="w-5 h-5 text-[#EF4444]" />
          </div>
        </div>
      </div>

      {/* Recurring Issue Alert Banner */}
      <div className="p-5 bg-[#FEF2F2] border border-[#F87171]/40 rounded-2xl space-y-3 shadow-xs">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-[#991B1B] font-heading font-bold text-sm">
            <AlertCircle className="w-4 h-4 text-[#EF4444]" />
            Recurring Issue Detected: High Delivery Delay Friction
          </div>
          <span className="px-2.5 py-0.5 rounded-full bg-[#EF4444] text-white font-semibold text-[10px]">
            1,284 Mentions (DEMO)
          </span>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-xs pt-1">
          <div>
            <span className="text-[#64748B] font-medium">Affected Category:</span>
            <div className="font-semibold text-[#18324A] mt-0.5">Shipping & Delivery</div>
          </div>
          <div>
            <span className="text-[#64748B] font-medium">Sentiment Impact:</span>
            <div className="font-semibold text-[#EF4444] mt-0.5">Negative (-0.78 score)</div>
          </div>
          <div>
            <span className="text-[#64748B] font-medium">Trend Period:</span>
            <div className="font-semibold text-[#991B1B] mt-0.5">↑ +18% this week</div>
          </div>
          <div>
            <span className="text-[#64748B] font-medium">AI Suggested Action:</span>
            <div className="font-semibold text-[#065F46] mt-0.5">Automate SLA alerts & re-shipment</div>
          </div>
        </div>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Sentiment Distribution Chart */}
        <div className="p-6 bg-white border border-[#E2E8F0] rounded-2xl space-y-4 shadow-xs">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-heading font-bold text-[#18324A] flex items-center gap-2">
              <Smile className="w-4 h-4 text-[#10B981]" />
              Customer Sentiment Ratio
            </h3>
            <span className="text-xs text-[#64748B]">Dataset Metrics</span>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={85}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {pieData.map((entry) => (
                    <Cell
                      key={`cell-${entry.name}`}
                      fill={SENTIMENT_COLORS[entry.name as keyof typeof SENTIMENT_COLORS]}
                    />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#FFFFFF', borderColor: '#E2E8F0', borderRadius: '12px', fontSize: '12px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}
                />
                <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Sentiment by Department */}
        <div className="p-6 bg-white border border-[#E2E8F0] rounded-2xl space-y-4 shadow-xs">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-heading font-bold text-[#18324A] flex items-center gap-2">
              <Building2 className="w-4 h-4 text-[#0284C7]" />
              Sentiment by Department
            </h3>
            <span className="text-xs text-[#64748B]">Class Breakdown</span>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={deptData}>
                <XAxis dataKey="department" stroke="#64748B" fontSize={11} tickLine={false} />
                <YAxis stroke="#64748B" fontSize={11} tickLine={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#FFFFFF', borderColor: '#E2E8F0', borderRadius: '12px', fontSize: '12px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}
                />
                <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
                <Bar dataKey="Positive" fill="#10B981" radius={[4, 4, 0, 0]} />
                <Bar dataKey="Neutral" fill="#0284C7" radius={[4, 4, 0, 0]} />
                <Bar dataKey="Negative" fill="#EF4444" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* AI Business Recommendations */}
      <div className="p-6 bg-white border border-[#E2E8F0] rounded-2xl space-y-4 shadow-xs">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-[#18324A] font-heading font-bold text-sm">
            <Sparkles className="w-4 h-4 text-[#0284C7]" />
            AI Business Insight & Playbook
          </div>
          <span className="px-2.5 py-0.5 rounded-full bg-[#E4F5EF] text-[#065F46] text-[10px] font-semibold border border-[#B8E0D2]">
            Priority: High
          </span>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs pt-1">
          <div className="p-4 bg-[#F8FAFC] rounded-xl border border-[#E2E8F0]">
            <span className="text-[#64748B] font-medium">Problem Identified:</span>
            <p className="text-[#18324A] font-semibold mt-1">Delivery-related negative friction in return requests.</p>
          </div>
          <div className="p-4 bg-[#F8FAFC] rounded-xl border border-[#E2E8F0]">
            <span className="text-[#64748B] font-medium">Measured Evidence:</span>
            <p className="text-[#18324A] font-semibold mt-1">1,842 review mentions with avg sentiment -0.74 score.</p>
          </div>
          <div className="p-4 bg-[#E4F5EF] rounded-xl border border-[#B8E0D2]">
            <span className="text-[#065F46] font-medium">AI Recommended Action:</span>
            <p className="text-[#065F46] font-semibold mt-1">Instant refund trigger on carrier scan (+18% CSAT impact).</p>
          </div>
        </div>
      </div>
    </div>
  );
};
