import React from 'react';
import type { AnalyticsOverview } from '../../types';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  Legend,
} from 'recharts';
import { BarChart3, HeartHandshake, Smile, Frown } from 'lucide-react';

interface SentimentViewProps {
  data: AnalyticsOverview | null;
}

export const SentimentView: React.FC<SentimentViewProps> = ({ data }) => {
  if (!data) return <div className="p-8 text-slate-400">Loading sentiment analytics...</div>;

  // Sentiment timeline mock trend data
  const timelineData = [
    { date: 'Mon', Positive: 42, Neutral: 35, Negative: 25 },
    { date: 'Tue', Positive: 48, Neutral: 30, Negative: 28 },
    { date: 'Wed', Positive: 38, Neutral: 40, Negative: 32 },
    { date: 'Thu', Positive: 55, Neutral: 28, Negative: 18 },
    { date: 'Fri', Positive: 50, Neutral: 32, Negative: 22 },
    { date: 'Sat', Positive: 62, Neutral: 25, Negative: 15 },
    { date: 'Sun', Positive: 58, Neutral: 28, Negative: 16 },
  ];

  const categoryData = Object.entries(data.category_sentiment || {}).map(([cat, counts]) => ({
    category: cat,
    Positive: counts.Positive || 0,
    Neutral: counts.Neutral || 0,
    Negative: counts.Negative || 0,
  }));

  const emotionData = Object.entries(data.emotion_distribution || {}).map(([emotion, count]) => ({
    emotion,
    count,
  }));

  return (
    <div className="p-6 bg-slate-950 min-h-screen text-slate-100 space-y-6">
      {/* Header Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="p-5 bg-slate-900 border border-slate-800 rounded-xl flex items-center justify-between">
          <div>
            <p className="text-xs text-slate-400">Positive Sentiment</p>
            <h3 className="text-2xl font-bold text-emerald-400 mt-1">{data.positive_count}</h3>
          </div>
          <Smile className="w-8 h-8 text-emerald-400/80" />
        </div>
        <div className="p-5 bg-slate-900 border border-slate-800 rounded-xl flex items-center justify-between">
          <div>
            <p className="text-xs text-slate-400">Neutral Sentiment</p>
            <h3 className="text-2xl font-bold text-indigo-400 mt-1">{data.neutral_count}</h3>
          </div>
          <HeartHandshake className="w-8 h-8 text-indigo-400/80" />
        </div>
        <div className="p-5 bg-slate-900 border border-slate-800 rounded-xl flex items-center justify-between">
          <div>
            <p className="text-xs text-slate-400">Negative Sentiment</p>
            <h3 className="text-2xl font-bold text-rose-400 mt-1">{data.negative_count}</h3>
          </div>
          <Frown className="w-8 h-8 text-rose-400/80" />
        </div>
      </div>

      {/* Sentiment Trend Area Chart */}
      <div className="p-5 bg-slate-900 border border-slate-800 rounded-xl space-y-4">
        <h3 className="text-base font-bold text-white flex items-center gap-2">
          <BarChart3 className="w-5 h-5 text-indigo-400" />
          7-Day Sentiment Volume Trajectory
        </h3>
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={timelineData}>
              <XAxis dataKey="date" stroke="#64748b" fontSize={11} />
              <YAxis stroke="#64748b" fontSize={11} />
              <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }} />
              <Legend />
              <Area type="monotone" dataKey="Positive" stackId="1" stroke="#10B981" fill="#10B981" fillOpacity={0.6} />
              <Area type="monotone" dataKey="Neutral" stackId="1" stroke="#6366F1" fill="#6366F1" fillOpacity={0.6} />
              <Area type="monotone" dataKey="Negative" stackId="1" stroke="#EF4444" fill="#EF4444" fillOpacity={0.6} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Category Breakdown & Emotion Breakdown Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Category Breakdown */}
        <div className="p-5 bg-slate-900 border border-slate-800 rounded-xl space-y-4">
          <h3 className="text-base font-bold text-white">Sentiment by Product Category</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={categoryData}>
                <XAxis dataKey="category" stroke="#64748b" fontSize={10} />
                <YAxis stroke="#64748b" fontSize={11} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }} />
                <Legend />
                <Bar dataKey="Positive" fill="#10B981" stackId="a" />
                <Bar dataKey="Neutral" fill="#6366F1" stackId="a" />
                <Bar dataKey="Negative" fill="#EF4444" stackId="a" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Emotion Distribution */}
        <div className="p-5 bg-slate-900 border border-slate-800 rounded-xl space-y-4">
          <h3 className="text-base font-bold text-white">Fine-Grained Emotion Breakdown</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={emotionData} layout="vertical">
                <XAxis type="number" stroke="#64748b" fontSize={11} />
                <YAxis dataKey="emotion" type="category" stroke="#64748b" fontSize={11} width={90} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }} />
                <Bar dataKey="count" fill="#06B6D4" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};
