import React from 'react';
import type { AnalyticsOverview } from '../../types';
import { Target, HelpCircle, RefreshCw, AlertTriangle, Sparkles, CheckCircle } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

interface IntentViewProps {
  data: AnalyticsOverview | null;
}

export const IntentView: React.FC<IntentViewProps> = ({ data }) => {
  if (!data) return <div className="p-8 text-slate-400">Loading intent breakdown...</div>;

  const intentList = Object.entries(data.intent_distribution || {}).map(([intent, count]) => ({
    intent,
    count,
  }));

  const intentGuides = [
    {
      intent: 'Refund/Return',
      icon: RefreshCw,
      color: 'text-amber-400',
      strategy: 'Automate carrier pickup validation and instant digital wallet credit.',
    },
    {
      intent: 'Order Tracking',
      icon: Target,
      color: 'text-indigo-400',
      strategy: 'Provide live webhook updates directly in chatbot without agent intervention.',
    },
    {
      intent: 'Complaint',
      icon: AlertTriangle,
      color: 'text-rose-400',
      strategy: 'Route to supervisor queue when sentiment score drops below -0.5.',
    },
    {
      intent: 'Product Query',
      icon: HelpCircle,
      color: 'text-cyan-400',
      strategy: 'Surface interactive catalog specifications and stock status dynamically.',
    },
    {
      intent: 'Praise',
      icon: Sparkles,
      color: 'text-emerald-400',
      strategy: 'Prompt satisfied customers for public store reviews and loyalty rewards.',
    },
  ];

  return (
    <div className="p-6 bg-slate-950 min-h-screen text-slate-100 space-y-6">
      {/* Intent Chart */}
      <div className="p-6 bg-slate-900 border border-slate-800 rounded-xl space-y-4">
        <h3 className="text-base font-bold text-white flex items-center gap-2">
          <Target className="w-5 h-5 text-indigo-400" />
          Retail Customer Intent Classification Matrix
        </h3>
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={intentList}>
              <XAxis dataKey="intent" stroke="#64748b" fontSize={11} />
              <YAxis stroke="#64748b" fontSize={11} />
              <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }} />
              <Bar dataKey="count" fill="#6366F1" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Automated Resolution Strategy Cards */}
      <div className="space-y-4">
        <h3 className="text-base font-bold text-white">Automated Intent Handling & Resolution Playbooks</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {intentGuides.map((guide, idx) => {
            const Icon = guide.icon;
            const count = data.intent_distribution?.[guide.intent] || 0;
            return (
              <div key={idx} className="p-5 bg-slate-900 border border-slate-800 rounded-xl space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2.5">
                    <Icon className={`w-5 h-5 ${guide.color}`} />
                    <h4 className="font-bold text-sm text-white">{guide.intent}</h4>
                  </div>
                  <span className="px-2 py-0.5 rounded text-xs font-bold bg-slate-800 text-slate-300">
                    {count} cases
                  </span>
                </div>
                <p className="text-xs text-slate-400 leading-relaxed">{guide.strategy}</p>
                <div className="pt-2 flex items-center gap-1 text-[11px] text-emerald-400 font-medium">
                  <CheckCircle className="w-3.5 h-3.5" /> Rule Engine Configured
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
