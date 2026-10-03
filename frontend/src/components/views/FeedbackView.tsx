import React, { useState, useEffect } from 'react';
import { feedbackApi, sentimentApi } from '../../services/api';
import { FeedbackItem, SentimentAnalysisResult } from '../../types';
import { MessageSquarePlus, Send, Filter, CheckCircle2 } from 'lucide-react';

export const FeedbackView: React.FC = () => {
  const [feedbackList, setFeedbackList] = useState<FeedbackItem[]>([]);
  const [inputText, setInputText] = useState('');
  const [customerName, setCustomerName] = useState('');
  const [category, setCategory] = useState('Electronics');
  const [source, setSource] = useState('review');
  const [analysisResult, setAnalysisResult] = useState<SentimentAnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);

  // Filters
  const [filterSentiment, setFilterSentiment] = useState<string>('All');

  const fetchFeedback = async () => {
    try {
      const data = await feedbackApi.list(
        filterSentiment !== 'All' ? { sentiment: filterSentiment } : undefined
      );
      setFeedbackList(data);
    } catch (err) {
      console.error('Error fetching feedback:', err);
    }
  };

  useEffect(() => {
    fetchFeedback();
  }, [filterSentiment]);

  const handleSubmitFeedback = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim()) return;

    setLoading(true);
    try {
      // Analyze text live
      const analysis = await sentimentApi.analyze(inputText);
      setAnalysisResult(analysis);

      // Submit feedback record
      await feedbackApi.submit({
        text: inputText,
        customer_name: customerName || 'Anonymous',
        source,
        category,
      });

      setInputText('');
      fetchFeedback();
    } catch (err) {
      console.error('Error submitting feedback:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 bg-slate-950 min-h-screen text-slate-100 space-y-6">
      {/* Submit Single Feedback Card */}
      <div className="p-6 bg-slate-900 border border-slate-800 rounded-xl space-y-4">
        <h3 className="text-base font-bold text-white flex items-center gap-2">
          <MessageSquarePlus className="w-5 h-5 text-indigo-400" />
          Real-Time Feedback Ingestion & Analysis
        </h3>

        <form onSubmit={handleSubmitFeedback} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1">Customer Identifier</label>
              <input
                type="text"
                value={customerName}
                onChange={(e) => setCustomerName(e.target.value)}
                placeholder="e.g. Customer #8821"
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1">Category</label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white"
              >
                <option value="Electronics">Electronics</option>
                <option value="Fashion">Fashion</option>
                <option value="Home & Kitchen">Home & Kitchen</option>
                <option value="Shipping & Delivery">Shipping & Delivery</option>
                <option value="Customer Support">Customer Support</option>
                <option value="Billing & Refunds">Billing & Refunds</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1">Source Channel</label>
              <select
                value={source}
                onChange={(e) => setSource(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white"
              >
                <option value="review">Product Review</option>
                <option value="chat">Chat Transcript</option>
                <option value="survey">NPS Survey</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-400 mb-1">Feedback Text</label>
            <textarea
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              rows={3}
              placeholder="Paste raw customer feedback, survey comment, or review..."
              className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
            />
          </div>

          <button
            type="submit"
            disabled={loading || !inputText.trim()}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-bold flex items-center gap-2 transition"
          >
            <Send className="w-3.5 h-3.5" /> Analyze & Save Feedback
          </button>
        </form>

        {/* Live Analysis Result */}
        {analysisResult && (
          <div className="p-4 bg-slate-950 border border-indigo-500/30 rounded-xl space-y-2 text-xs">
            <h4 className="font-bold text-indigo-400 flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" /> Real-Time Inference Output
            </h4>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2">
              <div>
                <span className="text-slate-400">Predicted Sentiment:</span>
                <p className="font-bold text-white">{analysisResult.sentiment}</p>
              </div>
              <div>
                <span className="text-slate-400">Sentiment Score:</span>
                <p className="font-bold text-white">{analysisResult.sentiment_score}</p>
              </div>
              <div>
                <span className="text-slate-400">Detected Intent:</span>
                <p className="font-bold text-cyan-300">{analysisResult.intent}</p>
              </div>
              <div>
                <span className="text-slate-400">Detected Emotion:</span>
                <p className="font-bold text-emerald-300">{analysisResult.emotion}</p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Filterable Table */}
      <div className="p-6 bg-slate-900 border border-slate-800 rounded-xl space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <h3 className="text-base font-bold text-white">Ingested Customer Feedback Directory</h3>
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-slate-400" />
            <select
              value={filterSentiment}
              onChange={(e) => setFilterSentiment(e.target.value)}
              className="bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-white"
            >
              <option value="All">All Sentiments</option>
              <option value="Positive">Positive Only</option>
              <option value="Neutral">Neutral Only</option>
              <option value="Negative">Negative Only</option>
            </select>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-950 text-slate-400 uppercase font-semibold border-b border-slate-800">
              <tr>
                <th className="p-3">Customer</th>
                <th className="p-3">Feedback Text</th>
                <th className="p-3">Category</th>
                <th className="p-3">Sentiment</th>
                <th className="p-3">Intent</th>
                <th className="p-3">Emotion</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {feedbackList.slice(0, 15).map((item) => (
                <tr key={item.id} className="hover:bg-slate-800/40">
                  <td className="p-3 font-semibold text-white">{item.customer_id}</td>
                  <td className="p-3 max-w-md truncate">{item.text}</td>
                  <td className="p-3 text-slate-400">{item.category}</td>
                  <td className="p-3">
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        item.sentiment === 'Positive'
                          ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                          : item.sentiment === 'Negative'
                          ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                          : 'bg-indigo-500/20 text-indigo-400 border border-indigo-500/30'
                      }`}
                    >
                      {item.sentiment}
                    </span>
                  </td>
                  <td className="p-3 text-cyan-300">{item.intent}</td>
                  <td className="p-3 text-slate-300">{item.emotion}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
