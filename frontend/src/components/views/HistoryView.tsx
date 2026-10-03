import React, { useEffect } from 'react';
import { chatApi } from '../../services/api';
import { History, MessageSquare } from 'lucide-react';

export const HistoryView: React.FC = () => {
  useEffect(() => {
    chatApi.createSession('Demo Customer').then(() => {
      // Load sample session history
    });
  }, []);

  return (
    <div className="p-6 bg-slate-950 min-h-screen text-slate-100 space-y-6">
      <div>
        <h3 className="text-xl font-bold text-white flex items-center gap-2">
          <History className="w-5 h-5 text-indigo-400" />
          Customer Conversation History & Arc Logs
        </h3>
        <p className="text-xs text-slate-400 mt-1">
          Review turn-by-turn customer chat transcripts, sentiment trajectories, and manager resolution history.
        </p>
      </div>

      <div className="p-6 bg-slate-900 border border-slate-800 rounded-xl space-y-4">
        <div className="flex items-center gap-2 text-xs text-slate-400">
          <MessageSquare className="w-4 h-4 text-indigo-400" />
          Active Chat Log Directory
        </div>

        <div className="p-4 bg-slate-950 border border-slate-800 rounded-lg text-xs space-y-2">
          <div className="flex justify-between items-center text-slate-300">
            <span>Customer: <strong>Sarah Jenkins</strong></span>
            <span className="text-emerald-400 font-semibold">Trajectory: Improving (-0.89 to +0.10)</span>
          </div>
          <p className="text-slate-400">Turn 1: "Charged twice for defective headphones!" -&gt; Turn 2: "Manager assigned, issue resolved."</p>
        </div>
      </div>
    </div>
  );
};
