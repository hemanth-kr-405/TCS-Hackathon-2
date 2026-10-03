import React from 'react';
import type { RecurringIssue } from '../../types';
import { AlertTriangle, CheckCircle2, Clock, Flame } from 'lucide-react';

interface RecurringIssuesViewProps {
  issues: RecurringIssue[];
}

export const RecurringIssuesView: React.FC<RecurringIssuesViewProps> = ({ issues }) => {
  return (
    <div className="p-6 bg-slate-950 min-h-screen text-slate-100 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h3 className="text-xl font-bold text-white flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-amber-400" />
            Recurring Customer Issue Intelligence
          </h3>
          <p className="text-xs text-slate-400 mt-1">
            Automatically extracted complaint patterns, cluster frequency, and sentiment impact scores.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {issues.map((issue) => (
          <div
            key={issue.id}
            className="p-5 bg-slate-900 border border-slate-800 rounded-xl space-y-4 hover:border-slate-700 transition"
          >
            <div className="flex items-start justify-between gap-3">
              <div>
                <span className="text-[10px] font-bold tracking-wider uppercase text-slate-500">
                  {issue.issue_key}
                </span>
                <h4 className="text-sm font-bold text-white mt-0.5">{issue.title}</h4>
              </div>
              <span
                className={`px-2.5 py-1 rounded text-xs font-bold ${
                  issue.severity === 'Critical'
                    ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                    : issue.severity === 'High'
                    ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                    : 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/30'
                }`}
              >
                {issue.severity}
              </span>
            </div>

            <p className="text-xs text-slate-400 leading-relaxed">{issue.description}</p>

            <div className="grid grid-cols-3 gap-2 pt-2 border-t border-slate-800/80 text-xs">
              <div>
                <span className="text-[11px] text-slate-500">Category</span>
                <p className="font-semibold text-slate-200 mt-0.5">{issue.category}</p>
              </div>
              <div>
                <span className="text-[11px] text-slate-500">Frequency</span>
                <p className="font-semibold text-amber-400 mt-0.5">{issue.frequency} reports</p>
              </div>
              <div>
                <span className="text-[11px] text-slate-500">Avg Sentiment</span>
                <p className="font-semibold text-rose-400 mt-0.5">{issue.average_sentiment}</p>
              </div>
            </div>

            <div className="flex items-center justify-between pt-2">
              <span className="text-xs text-slate-400 flex items-center gap-1.5">
                {issue.status === 'Resolved' ? (
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                ) : issue.status === 'In Progress' ? (
                  <Clock className="w-4 h-4 text-amber-400 animate-spin" />
                ) : (
                  <Flame className="w-4 h-4 text-rose-400" />
                )}
                Status: <strong className="text-white">{issue.status}</strong>
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
