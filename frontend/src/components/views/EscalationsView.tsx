import React, { useState } from 'react';
import type { EscalationItem } from '../../types';
import { escalationsApi } from '../../services/api';
import { ShieldAlert, UserCheck, CheckCircle2 } from 'lucide-react';

interface EscalationsViewProps {
  escalations: EscalationItem[];
  onRefresh?: () => void;
}

export const EscalationsView: React.FC<EscalationsViewProps> = ({ escalations, onRefresh }) => {
  const [updatingId, setUpdatingId] = useState<number | null>(null);

  const handleUpdateStatus = async (id: number, status: string) => {
    setUpdatingId(id);
    try {
      await escalationsApi.update(id, { status });
      if (onRefresh) onRefresh();
    } catch (err) {
      console.error('Error updating escalation:', err);
    } finally {
      setUpdatingId(null);
    }
  };

  return (
    <div className="p-6 bg-[#F5F5F5] min-h-screen text-[#18324A] space-y-6 fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white border border-[#E2E8F0] p-6 rounded-2xl shadow-xs">
        <div>
          <h3 className="text-xl font-heading font-bold text-[#18324A] flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 text-[#EF4444]" />
            Supervisor Escalation Management Queue
          </h3>
          <p className="text-xs text-[#64748B] mt-1 font-medium">
            Cases automatically flagged due to high customer anger, low sentiment scores (&lt; -0.4), or supervisor requests.
          </p>
        </div>
      </div>

      <div className="space-y-4">
        {(escalations || []).length === 0 ? (
          <div className="p-8 bg-white border border-[#E2E8F0] rounded-2xl text-center text-[#64748B] text-xs font-medium shadow-xs">
            No active escalations. All customer chats are within healthy sentiment parameters.
          </div>
        ) : (
          (escalations || []).map((item) => (
            <div
              key={item.id}
              className="p-5 bg-white border border-[#E2E8F0] rounded-2xl space-y-3 flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-xs"
            >
              <div className="space-y-1.5 max-w-2xl text-xs">
                <div className="flex items-center gap-2.5">
                  <span
                    className={`px-2.5 py-0.5 rounded-full text-[10px] font-semibold ${
                      item.severity === 'Critical'
                        ? 'bg-[#FEF2F2] text-[#EF4444] border border-[#F87171]/40'
                        : 'bg-[#FFFBEB] text-[#D97706] border border-[#FBBF24]/40'
                    }`}
                  >
                    {item.severity} Urgency
                  </span>
                  <span className="text-[#64748B]">Session ID: {item.session_id}</span>
                  <span className="font-bold text-[#18324A]">Customer: {item.customer_name}</span>
                </div>

                <p className="text-[#18324A] leading-relaxed">
                  <strong>Trigger Reason:</strong> {item.reason}
                </p>

                <div className="flex items-center gap-4 text-[11px] text-[#64748B] pt-1">
                  <span>Sentiment Score: <strong className="text-[#EF4444]">{item.sentiment_score}</strong></span>
                  <span>Assigned Agent: <strong className="text-[#0284C7]">{item.assigned_agent}</strong></span>
                </div>
              </div>

              <div className="flex items-center gap-2">
                {item.status !== 'Resolved' && (
                  <button
                    onClick={() => handleUpdateStatus(item.id, 'Resolved')}
                    disabled={updatingId === item.id}
                    className="px-3.5 py-1.5 bg-[#065F46] hover:bg-[#044E38] text-white text-xs font-semibold rounded-xl flex items-center gap-1.5 transition shadow-xs"
                  >
                    <CheckCircle2 className="w-3.5 h-3.5" /> Mark Resolved
                  </button>
                )}
                {item.status === 'Pending' && (
                  <button
                    onClick={() => handleUpdateStatus(item.id, 'Reviewed')}
                    disabled={updatingId === item.id}
                    className="px-3.5 py-1.5 bg-[#18324A] hover:bg-[#0F2232] text-white text-xs font-semibold rounded-xl flex items-center gap-1.5 transition shadow-xs"
                  >
                    <UserCheck className="w-3.5 h-3.5 text-[#B8E0D2]" /> Take Action
                  </button>
                )}
                {item.status === 'Resolved' && (
                  <span className="px-3 py-1 text-xs font-semibold bg-[#E4F5EF] text-[#065F46] border border-[#B8E0D2] rounded-xl">
                    Resolved
                  </span>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
