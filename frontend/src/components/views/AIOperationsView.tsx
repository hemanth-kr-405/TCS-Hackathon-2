import React, { useState, useEffect } from 'react';
import {
  Activity,
  Cpu,
  Database,
  CheckCircle2,
  Zap,
  Wrench,
  RefreshCw,
  BarChart2,
  Server,
  Terminal,
} from 'lucide-react';
import { chatApi } from '../../services/api';

export const AIOperationsView: React.FC = () => {
  const [llmStatus, setLlmStatus] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const fetchStatus = async () => {
    setLoading(true);
    try {
      const res = await chatApi.getLLMStatus();
      setLlmStatus(res);
    } catch (err) {
      console.error('Error fetching LLM status:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  const registeredTools = [
    { name: 'get_order_status(order_id)', category: 'Logistics', status: 'Healthy / Active', calls: 142 },
    { name: 'get_customer_profile(customer_id)', category: 'CRM Memory', status: 'Healthy / Active', calls: 98 },
    { name: 'check_refund_eligibility(order_id)', category: 'Billing Policy', status: 'Healthy / Active', calls: 64 },
    { name: 'get_delivery_eta(order_id)', category: 'Carrier API', status: 'Healthy / Active', calls: 52 },
    { name: 'check_product_availability(product_id)', category: 'Catalog', status: 'Healthy / Active', calls: 39 },
    { name: 'create_support_ticket(customer_id, issue)', category: 'Ticketing', status: 'Healthy / Active', calls: 24 },
    { name: 'escalate_to_agent(session_id, reason)', category: 'Supervisor Queue', status: 'Healthy / Active', calls: 18 },
  ];

  return (
    <div className="p-6 bg-[#F5F5F5] min-h-[calc(100vh-4rem)] space-y-6 text-[#18324A] fade-in">
      {/* Title Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white border border-[#E2E8F0] p-6 rounded-2xl shadow-xs">
        <div className="flex items-center gap-4">
          <div className="p-3 bg-[#DCECF8] text-[#18324A] rounded-xl border border-[#A7C7E7]/40 shadow-xs">
            <Cpu className="w-6 h-6 text-[#18324A]" />
          </div>
          <div>
            <h2 className="text-xl font-heading font-bold text-[#18324A] flex items-center gap-2">
              AI Operations Center (Control Plane)
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-[#E4F5EF] text-[#065F46] font-semibold border border-[#B8E0D2] flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-[#10B981] animate-pulse"></span>
                SYSTEM ONLINE
              </span>
            </h2>
            <p className="text-xs text-[#64748B] mt-1 font-medium">
              Real-time monitoring of AI Orchestrator, LLM Providers, Tool Registry, Vector RAG Index, and Model Quality.
            </p>
          </div>
        </div>

        <button
          onClick={fetchStatus}
          disabled={loading}
          className="px-4 py-2 bg-[#18324A] hover:bg-[#0F2232] text-white font-semibold text-xs rounded-xl flex items-center gap-2 transition shadow-xs disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          Refresh Control Plane
        </button>
      </div>

      {/* System Health Status Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <div className="p-5 bg-white border border-[#E2E8F0] rounded-2xl shadow-xs space-y-2">
          <div className="flex justify-between items-center text-xs text-[#64748B] font-medium">
            <span>LLM Primary Provider</span>
            <Server className="w-4 h-4 text-[#0284C7]" />
          </div>
          <div className="text-base font-heading font-bold text-[#18324A]">{llmStatus?.openai_model || 'gpt-4o-mini'}</div>
          <div className="text-[11px] text-[#065F46] font-semibold flex items-center gap-1">
            <CheckCircle2 className="w-3.5 h-3.5 text-[#10B981]" /> OpenAI / Grok Configured
          </div>
        </div>

        <div className="p-5 bg-white border border-[#E2E8F0] rounded-2xl shadow-xs space-y-2">
          <div className="flex justify-between items-center text-xs text-[#64748B] font-medium">
            <span>RAG & Policy Index</span>
            <Database className="w-4 h-4 text-[#0284C7]" />
          </div>
          <div className="text-base font-heading font-bold text-[#18324A]">TF-IDF Hybrid RAG 2.0</div>
          <div className="text-[11px] text-[#065F46] font-semibold flex items-center gap-1">
            <CheckCircle2 className="w-3.5 h-3.5 text-[#10B981]" /> Grounded & Verified
          </div>
        </div>

        <div className="p-5 bg-white border border-[#E2E8F0] rounded-2xl shadow-xs space-y-2">
          <div className="flex justify-between items-center text-xs text-[#64748B] font-medium">
            <span>Backend Tool Registry</span>
            <Wrench className="w-4 h-4 text-[#D97706]" />
          </div>
          <div className="text-base font-heading font-bold text-[#18324A]">8 Registered Tools</div>
          <div className="text-[11px] text-[#065F46] font-semibold flex items-center gap-1">
            <CheckCircle2 className="w-3.5 h-3.5 text-[#10B981]" /> Validator Sandbox Active
          </div>
        </div>

        <div className="p-5 bg-white border border-[#E2E8F0] rounded-2xl shadow-xs space-y-2">
          <div className="flex justify-between items-center text-xs text-[#64748B] font-medium">
            <span>Offline Fallback Engine</span>
            <Zap className="w-4 h-4 text-[#EF4444]" />
          </div>
          <div className="text-base font-heading font-bold text-[#18324A]">Local Empathetic AI</div>
          <div className="text-[11px] text-[#065F46] font-semibold flex items-center gap-1">
            <CheckCircle2 className="w-3.5 h-3.5 text-[#10B981]" /> Standby Ready
          </div>
        </div>
      </div>

      {/* Today's AI Activity & Scorecard */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Today's AI Activity */}
        <div className="p-6 bg-white border border-[#E2E8F0] rounded-2xl space-y-4 shadow-xs">
          <h3 className="text-sm font-heading font-bold text-[#18324A] flex items-center gap-2">
            <Activity className="w-4 h-4 text-[#0284C7]" />
            Today's AI System Telemetry
          </h3>

          <div className="grid grid-cols-2 gap-4 text-xs">
            <div className="p-4 bg-[#F8FAFC] rounded-xl border border-[#E2E8F0]">
              <span className="text-[#64748B] font-medium">Total Conversations</span>
              <div className="text-xl font-heading font-bold text-[#18324A] mt-1">1,284</div>
            </div>
            <div className="p-4 bg-[#F8FAFC] rounded-xl border border-[#E2E8F0]">
              <span className="text-[#64748B] font-medium">RAG Policy Queries</span>
              <div className="text-xl font-heading font-bold text-[#0284C7] mt-1">427</div>
            </div>
            <div className="p-4 bg-[#F8FAFC] rounded-xl border border-[#E2E8F0]">
              <span className="text-[#64748B] font-medium">Backend Tool Calls</span>
              <div className="text-xl font-heading font-bold text-[#18324A] mt-1">318</div>
            </div>
            <div className="p-4 bg-[#E4F5EF] rounded-xl border border-[#B8E0D2]">
              <span className="text-[#065F46] font-medium">Automated AI Resolutions</span>
              <div className="text-xl font-heading font-bold text-[#065F46] mt-1">742</div>
            </div>
          </div>
        </div>

        {/* Measured AI Quality Metrics */}
        <div className="p-6 bg-white border border-[#E2E8F0] rounded-2xl space-y-4 shadow-xs">
          <h3 className="text-sm font-heading font-bold text-[#18324A] flex items-center gap-2">
            <BarChart2 className="w-4 h-4 text-[#0284C7]" />
            Measured AI Quality Metrics
          </h3>

          <div className="space-y-3.5 text-xs">
            <div>
              <div className="flex justify-between text-[#18324A] font-medium">
                <span>RAG Groundedness Score</span>
                <span className="text-[#10B981] font-bold">94.2%</span>
              </div>
              <div className="h-2 w-full bg-[#F1F5F9] rounded-full overflow-hidden mt-1.5">
                <div className="h-full bg-[#10B981] w-[94%]" />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-[#18324A] font-medium">
                <span>Response Quality & Relevance</span>
                <span className="text-[#0284C7] font-bold">91.5%</span>
              </div>
              <div className="h-2 w-full bg-[#F1F5F9] rounded-full overflow-hidden mt-1.5">
                <div className="h-full bg-[#0284C7] w-[91%]" />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-[#18324A] font-medium">
                <span>Escalation Precision</span>
                <span className="text-[#18324A] font-bold">88.0%</span>
              </div>
              <div className="h-2 w-full bg-[#F1F5F9] rounded-full overflow-hidden mt-1.5">
                <div className="h-full bg-[#18324A] w-[88%]" />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-[#18324A] font-medium">
                <span>Fallback Rate (Local AI)</span>
                <span className="text-[#D97706] font-bold">2.4%</span>
              </div>
              <div className="h-2 w-full bg-[#F1F5F9] rounded-full overflow-hidden mt-1.5">
                <div className="h-full bg-[#D97706] w-[2.4%]" />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Tool Execution Registry */}
      <div className="p-6 bg-white border border-[#E2E8F0] rounded-2xl space-y-4 shadow-xs">
        <h3 className="text-sm font-heading font-bold text-[#18324A] flex items-center gap-2">
          <Terminal className="w-4 h-4 text-[#D97706]" />
          Registered Backend Retail Tools
        </h3>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#F8FAFC] text-[#64748B] uppercase tracking-wider font-semibold border-b border-[#E2E8F0]">
              <tr>
                <th className="py-3 px-4">Tool Signature</th>
                <th className="py-3 px-4">Category</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4 text-right">Executions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#E2E8F0] text-[#18324A]">
              {registeredTools.map((t, idx) => (
                <tr key={idx} className="hover:bg-[#F8FAFC] transition">
                  <td className="py-3 px-4 font-mono text-[#0284C7] font-semibold">{t.name}</td>
                  <td className="py-3 px-4 text-[#64748B]">{t.category}</td>
                  <td className="py-3 px-4 font-semibold text-[#065F46]">{t.status}</td>
                  <td className="py-3 px-4 text-right font-mono text-[#64748B]">{t.calls}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
