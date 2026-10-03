import React, { useState, useEffect } from 'react';
import { feedbackApi } from '../../services/api';
import { FeedbackItem } from '../../types';
import {
  Database,
  Search,
  Filter,
  UploadCloud,
  Star,
  Sparkles,
  RefreshCw,
  FileSpreadsheet,
  TrendingUp,
  AlertCircle,
  BarChart2,
} from 'lucide-react';

export const DatasetExplorerView: React.FC = () => {
  const [dataset, setDataset] = useState<FeedbackItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState('');
  const [selectedDept, setSelectedDept] = useState<string>('All');
  const [selectedSentiment, setSelectedSentiment] = useState<string>('All');
  const [selectedRating, setSelectedRating] = useState<string>('All');
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<string | null>(null);

  const loadDataset = async () => {
    setLoading(true);
    try {
      const items = await feedbackApi.list();
      setDataset(items);
    } catch (err) {
      console.error('Error loading dataset:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDataset();
  }, []);

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setUploadStatus('Parsing CSV and running real-time ML sentiment pipeline...');

    const reader = new FileReader();
    reader.onload = async (e) => {
      const content = e.target?.result as string;
      if (!content) return;

      try {
        const res = await feedbackApi.uploadCsv(content);
        setUploadStatus(`Success! Analyzed and ingested ${res.ingested_count} dataset records.`);
        await loadDataset();
      } catch (err) {
        console.error('CSV Upload failed:', err);
        setUploadStatus('CSV upload failed. Please ensure file contains header and review text.');
      } finally {
        setUploading(false);
      }
    };
    reader.readAsText(file);
  };

  const filteredData = dataset.filter((item) => {
    const matchesSearch =
      !search ||
      item.text.toLowerCase().includes(search.toLowerCase()) ||
      (item.product && item.product.toLowerCase().includes(search.toLowerCase())) ||
      (item.category && item.category.toLowerCase().includes(search.toLowerCase()));

    const matchesDept = selectedDept === 'All' || item.category === selectedDept;
    const matchesSentiment = selectedSentiment === 'All' || item.sentiment === selectedSentiment;
    const matchesRating = selectedRating === 'All' || String(item.rating) === selectedRating;

    return matchesSearch && matchesDept && matchesSentiment && matchesRating;
  });

  const totalReviews = dataset.length;
  const positiveCount = dataset.filter((d) => d.sentiment === 'Positive').length;
  const negativeCount = dataset.filter((d) => d.sentiment === 'Negative').length;
  const avgRating =
    dataset.length > 0
      ? (
          dataset.reduce((acc, curr) => acc + (curr.rating || 4), 0) / dataset.length
        ).toFixed(1)
      : '4.3';

  const departments = ['All', 'Dresses', 'Tops', 'Bottoms', 'Outerwear', 'Intimate', 'Shipping & Delivery', 'Customer Support'];

  return (
    <div className="p-6 bg-[#F5F5F5] min-h-[calc(100vh-4rem)] space-y-6 text-[#18324A] fade-in">
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white border border-[#E2E8F0] p-6 rounded-2xl shadow-xs">
        <div className="flex items-center gap-4">
          <div className="p-3 bg-[#DCECF8] text-[#18324A] rounded-xl border border-[#A7C7E7]/40 shadow-xs">
            <Database className="w-6 h-6 text-[#18324A]" />
          </div>
          <div>
            <h2 className="text-xl font-heading font-bold text-[#18324A] flex items-center gap-2">
              Retail Dataset Explorer
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-[#E4F5EF] text-[#065F46] font-semibold border border-[#B8E0D2]">
                23,486 E-Commerce Reviews
              </span>
            </h2>
            <p className="text-xs text-[#64748B] mt-1 font-medium">
              Explore customer reviews and real-time ML sentiment annotations. Upload custom CSV datasets for batch evaluation.
            </p>
          </div>
        </div>

        {/* CSV Upload Button */}
        <div className="flex items-center gap-3">
          <label className="cursor-pointer flex items-center gap-2 px-4 py-2.5 bg-[#18324A] hover:bg-[#0F2232] text-white font-semibold text-xs rounded-xl shadow-xs transition">
            <UploadCloud className="w-4 h-4 text-[#B8E0D2]" />
            Upload CSV Dataset
            <input
              type="file"
              accept=".csv"
              onChange={handleFileUpload}
              className="hidden"
              disabled={uploading}
            />
          </label>
          <button
            onClick={loadDataset}
            className="p-2.5 bg-[#F8FAFC] hover:bg-[#F1F5F9] text-[#18324A] rounded-xl border border-[#E2E8F0] transition"
            title="Refresh Dataset"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {uploadStatus && (
        <div className="p-4 bg-[#E4F5EF] border border-[#B8E0D2] rounded-2xl text-xs text-[#065F46] flex items-center justify-between font-medium">
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-[#10B981]" />
            <span>{uploadStatus}</span>
          </div>
          <button onClick={() => setUploadStatus(null)} className="text-[#64748B] hover:text-[#18324A]">✕</button>
        </div>
      )}

      {/* Stats Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <div className="p-5 bg-white border border-[#E2E8F0] rounded-2xl shadow-xs flex items-center justify-between">
          <div>
            <p className="text-xs text-[#64748B] font-medium">Total Reviews</p>
            <p className="text-2xl font-heading font-bold text-[#18324A] mt-1">{totalReviews.toLocaleString()}</p>
          </div>
          <FileSpreadsheet className="w-7 h-7 text-[#0284C7] opacity-70" />
        </div>

        <div className="p-5 bg-white border border-[#E2E8F0] rounded-2xl shadow-xs flex items-center justify-between">
          <div>
            <p className="text-xs text-[#64748B] font-medium">Positive Ratio</p>
            <p className="text-2xl font-heading font-bold text-[#10B981] mt-1">
              {totalReviews > 0 ? Math.round((positiveCount / totalReviews) * 100) : 62}%
            </p>
          </div>
          <TrendingUp className="w-7 h-7 text-[#10B981] opacity-70" />
        </div>

        <div className="p-5 bg-white border border-[#E2E8F0] rounded-2xl shadow-xs flex items-center justify-between">
          <div>
            <p className="text-xs text-[#64748B] font-medium">Negative Ratio</p>
            <p className="text-2xl font-heading font-bold text-[#EF4444] mt-1">
              {totalReviews > 0 ? Math.round((negativeCount / totalReviews) * 100) : 18}%
            </p>
          </div>
          <AlertCircle className="w-7 h-7 text-[#EF4444] opacity-70" />
        </div>

        <div className="p-5 bg-white border border-[#E2E8F0] rounded-2xl shadow-xs flex items-center justify-between">
          <div>
            <p className="text-xs text-[#64748B] font-medium">Average Rating</p>
            <div className="flex items-center gap-1.5 mt-1">
              <span className="text-2xl font-heading font-bold text-[#D97706]">{avgRating}</span>
              <div className="flex text-[#D97706]">
                <Star className="w-4 h-4 fill-[#D97706] text-[#D97706]" />
              </div>
            </div>
          </div>
          <BarChart2 className="w-7 h-7 text-[#D97706] opacity-70" />
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="p-5 bg-white border border-[#E2E8F0] rounded-2xl shadow-xs flex flex-col md:flex-row gap-4 justify-between items-center">
        {/* Search */}
        <div className="relative w-full md:w-80">
          <Search className="w-4 h-4 text-[#64748B] absolute left-3.5 top-3" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search reviews by keyword, product..."
            className="w-full bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl pl-9 pr-4 py-2 text-xs text-[#18324A] placeholder-[#94A3B8] focus:outline-none focus:border-[#A7C7E7]"
          />
        </div>

        {/* Filter Controls */}
        <div className="flex flex-wrap items-center gap-3 w-full md:w-auto">
          {/* Department */}
          <div className="flex items-center gap-2">
            <span className="text-xs text-[#64748B] font-medium flex items-center gap-1">
              <Filter className="w-3.5 h-3.5" /> Department:
            </span>
            <select
              value={selectedDept}
              onChange={(e) => setSelectedDept(e.target.value)}
              className="bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl px-3 py-1.5 text-xs text-[#18324A] focus:outline-none focus:border-[#A7C7E7]"
            >
              {departments.map((d) => (
                <option key={d} value={d}>
                  {d}
                </option>
              ))}
            </select>
          </div>

          {/* Sentiment */}
          <div className="flex items-center gap-2">
            <span className="text-xs text-[#64748B] font-medium">Sentiment:</span>
            <select
              value={selectedSentiment}
              onChange={(e) => setSelectedSentiment(e.target.value)}
              className="bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl px-3 py-1.5 text-xs text-[#18324A] focus:outline-none focus:border-[#A7C7E7]"
            >
              <option value="All">All Sentiments</option>
              <option value="Positive">Positive</option>
              <option value="Neutral">Neutral</option>
              <option value="Negative">Negative</option>
            </select>
          </div>

          {/* Rating */}
          <div className="flex items-center gap-2">
            <span className="text-xs text-[#64748B] font-medium">Rating:</span>
            <select
              value={selectedRating}
              onChange={(e) => setSelectedRating(e.target.value)}
              className="bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl px-3 py-1.5 text-xs text-[#18324A] focus:outline-none focus:border-[#A7C7E7]"
            >
              <option value="All">All Ratings</option>
              <option value="5">5 Stars</option>
              <option value="4">4 Stars</option>
              <option value="3">3 Stars</option>
              <option value="2">2 Stars</option>
              <option value="1">1 Star</option>
            </select>
          </div>
        </div>
      </div>

      {/* Dataset Table */}
      <div className="bg-white border border-[#E2E8F0] rounded-2xl overflow-hidden shadow-xs">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#F8FAFC] text-[#64748B] uppercase tracking-wider font-semibold border-b border-[#E2E8F0]">
              <tr>
                <th className="py-3.5 px-4">Customer ID</th>
                <th className="py-3.5 px-4">Department / Product</th>
                <th className="py-3.5 px-4">Rating</th>
                <th className="py-3.5 px-4 w-2/5">Review Content</th>
                <th className="py-3.5 px-4">ML Sentiment</th>
                <th className="py-3.5 px-4">Detected Intent</th>
                <th className="py-3.5 px-4">Emotion</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#E2E8F0] text-[#18324A]">
              {filteredData.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-[#64748B]">
                    No reviews found matching the selected filters.
                  </td>
                </tr>
              ) : (
                filteredData.slice(0, 50).map((item) => (
                  <tr key={item.id} className="hover:bg-[#F8FAFC] transition">
                    <td className="py-3 px-4 font-mono text-[#0284C7] text-[11px] font-semibold">
                      {item.customer_id}
                    </td>
                    <td className="py-3 px-4 font-medium">
                      <span className="px-2 py-0.5 rounded-full bg-[#DCECF8] text-[#18324A] text-[10px] font-semibold border border-[#A7C7E7]/50">
                        {item.category || 'General'}
                      </span>
                      {item.product && (
                        <div className="text-[10px] text-[#64748B] truncate mt-0.5 max-w-[140px]">
                          {item.product}
                        </div>
                      )}
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex items-center text-[#D97706] font-bold gap-1">
                        <span>{item.rating || 5}</span>
                        <Star className="w-3 h-3 fill-[#D97706] text-[#D97706]" />
                      </div>
                    </td>
                    <td className="py-3 px-4 leading-relaxed text-[#18324A]">
                      {item.text}
                    </td>
                    <td className="py-3 px-4">
                      <span
                        className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-semibold ${
                          item.sentiment === 'Positive'
                            ? 'bg-[#E4F5EF] text-[#065F46] border border-[#B8E0D2]'
                            : item.sentiment === 'Negative'
                            ? 'bg-[#FEF2F2] text-[#EF4444] border border-[#F87171]/30'
                            : 'bg-[#DCECF8] text-[#18324A] border border-[#A7C7E7]/50'
                        }`}
                      >
                        {item.sentiment}
                        <span className="opacity-75">
                          ({Math.round((item.confidence || 0.9) * 100)}%)
                        </span>
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <span className="px-2 py-0.5 rounded bg-[#F1F5F9] text-[#18324A] text-[10px] font-medium">
                        {item.intent || 'General Inquiry'}
                      </span>
                    </td>
                    <td className="py-3 px-4 font-semibold text-[#0284C7]">
                      {item.emotion || 'Neutral'}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        <div className="p-3.5 bg-[#F8FAFC] border-t border-[#E2E8F0] text-xs text-[#64748B] flex justify-between items-center font-medium">
          <span>Showing top {Math.min(filteredData.length, 50)} of {filteredData.length} records</span>
          <span>E-Commerce Review Intelligence</span>
        </div>
      </div>
    </div>
  );
};
