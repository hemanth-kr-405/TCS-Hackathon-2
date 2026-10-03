import React, { useState } from 'react';
import { Settings, Database, Cpu } from 'lucide-react';

export const SettingsView: React.FC = () => {
  const [apiUrl, setApiUrl] = useState('http://localhost:8000/api');

  return (
    <div className="p-6 bg-slate-950 min-h-screen text-slate-100 space-y-6">
      <div>
        <h3 className="text-xl font-bold text-white flex items-center gap-2">
          <Settings className="w-5 h-5 text-indigo-400" />
          Platform Configuration & Settings
        </h3>
        <p className="text-xs text-slate-400 mt-1">
          Manage API endpoint base URLs, model selection modes, and environment preferences.
        </p>
      </div>

      <div className="p-6 bg-slate-900 border border-slate-800 rounded-xl space-y-6 max-w-2xl">
        <div className="space-y-2">
          <label className="block text-xs font-semibold text-slate-300">FastAPI Backend Endpoint</label>
          <input
            type="text"
            value={apiUrl}
            onChange={(e) => setApiUrl(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-xs text-white"
          />
        </div>

        <div className="space-y-2 pt-4 border-t border-slate-800">
          <h4 className="text-sm font-bold text-white flex items-center gap-2">
            <Cpu className="w-4 h-4 text-indigo-400" /> Active Architecture Mode
          </h4>
          <p className="text-xs text-slate-400 leading-relaxed">
            Current Baseline Engine: <strong>TF-IDF Vectorizer + Logistic Regression</strong> with full Transformer-compatible modular interfaces ready for HuggingFace / BERT models.
          </p>
        </div>

        <div className="space-y-2 pt-4 border-t border-slate-800">
          <h4 className="text-sm font-bold text-white flex items-center gap-2">
            <Database className="w-4 h-4 text-cyan-400" /> Database Engine Status
          </h4>
          <p className="text-xs text-slate-400 leading-relaxed">
            Connected to SQLite database file (<code className="text-cyan-300">retail_sentiment.db</code>) via SQLAlchemy ORM with PostgreSQL production migration compatibility.
          </p>
        </div>
      </div>
    </div>
  );
};
