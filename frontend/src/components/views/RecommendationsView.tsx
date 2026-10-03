import React from 'react';
import type { BusinessRecommendation } from '../../types';
import { Lightbulb, TrendingUp } from 'lucide-react';

interface RecommendationsViewProps {
  recommendations: BusinessRecommendation[];
}

export const RecommendationsView: React.FC<RecommendationsViewProps> = ({ recommendations }) => {
  return (
    <div className="p-6 bg-slate-950 min-h-screen text-slate-100 space-y-6">
      <div>
        <h3 className="text-xl font-bold text-white flex items-center gap-2">
          <Lightbulb className="w-5 h-5 text-cyan-400" />
          AI-Generated Actionable Business Recommendations
        </h3>
        <p className="text-xs text-slate-400 mt-1">
          Automated retail operational playbooks derived from sentiment patterns and recurring customer complaints.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {recommendations.map((rec) => (
          <div key={rec.id} className="p-5 bg-slate-900 border border-slate-800 rounded-xl space-y-4 flex flex-col justify-between">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-bold tracking-wider uppercase text-cyan-400">{rec.category}</span>
                <span
                  className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                    rec.priority === 'Critical'
                      ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                      : rec.priority === 'High'
                      ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                      : 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/30'
                  }`}
                >
                  {rec.priority} Priority
                </span>
              </div>

              <h4 className="text-sm font-bold text-white leading-snug">{rec.title}</h4>
              <p className="text-xs text-slate-400 leading-relaxed">{rec.description}</p>
            </div>

            <div className="pt-3 border-t border-slate-800 space-y-2">
              <div className="flex items-center gap-1.5 text-xs text-emerald-400 font-semibold">
                <TrendingUp className="w-4 h-4" /> Expected Impact: {rec.estimated_impact}
              </div>
              <div className="flex items-center justify-between text-xs text-slate-400 pt-1">
                <span>Status: <strong className="text-white">{rec.status}</strong></span>
                <span className="text-[10px] bg-slate-800 text-slate-300 px-2 py-0.5 rounded">Actionable</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
