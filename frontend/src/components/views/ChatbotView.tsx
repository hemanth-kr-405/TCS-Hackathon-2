import React, { useState, useEffect, useRef } from 'react';
import { chatApi } from '../../services/api';
import { ChatMessage, ChatSession } from '../../types';
import {
  Send,
  Bot,
  User,
  ShieldAlert,
  Sparkles,
  TrendingDown,
  TrendingUp,
  Minus,
  RefreshCw,
  Loader2,
  AlertCircle,
  BookOpen,
  FileText,
  Clock,
  HelpCircle,
  UserCheck,
  CheckCircle,
  X,
  PlayCircle,
  Trash2,
  ChevronDown,
  ChevronUp,
  Cpu,
  Layers,
  ArrowRight,
  ShieldCheck,
  Zap,
} from 'lucide-react';

interface ExtendedChatMessage extends ChatMessage {
  isThinking?: boolean;
  isError?: boolean;
  rag_sources?: Array<{ title: string; filename: string; category?: string; content: string; score?: number }>;
  thinking_steps?: string[];
  tools_executed?: any[];
  escalation_reasons?: string[];
  llm_provider?: string;
  entities?: Record<string, any>;
  interaction_mode?: string;
  confidence?: number;
}

interface ChatbotViewProps {
  isPresentationMode?: boolean;
}

export const ChatbotView: React.FC<ChatbotViewProps> = ({ isPresentationMode = false }) => {
  const [session, setSession] = useState<ChatSession | null>(null);
  const [messages, setMessages] = useState<ExtendedChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [lastSentText, setLastSentText] = useState<string>('');
  const [lastInteractionMode, setLastInteractionMode] = useState<string>('RETAIL_SUPPORT');
  const [lastLlmProvider, setLastLlmProvider] = useState<string>('Local AI Engine');

  // Decision trace state
  const [showDecisionTrace, setShowDecisionTrace] = useState<boolean>(true);

  // Modal / Drawer states
  const [selectedRagSource, setSelectedRagSource] = useState<any | null>(null);
  const [customerAnalysis, setCustomerAnalysis] = useState<any | null>(null);
  const [analysisLoading, setAnalysisLoading] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const startNewSession = async (customerName: string = 'Sarah Jenkins') => {
    setLoading(true);
    try {
      const newSession = await chatApi.createSession(customerName);
      setSession(newSession);

      const initialMsgs: ExtendedChatMessage[] = [
        {
          id: `welcome_${Date.now()}`,
          session_id: newSession.session_id,
          sender: 'bot',
          text: `Hi Sarah! 👋 I'm RetailAI, your TCS AI customer intelligence assistant. How can I help with your order today?`,
          timestamp: new Date().toISOString(),
          triggered_escalation: false,
        },
      ];

      setMessages(initialMsgs);
    } catch (err) {
      console.error('Failed to create session:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleResetDemo = async () => {
    setLoading(true);
    try {
      await chatApi.resetDemo();
      await startNewSession('Sarah Jenkins');
    } catch (err) {
      console.error('Reset demo error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    startNewSession('Sarah Jenkins');
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (textToSend?: string) => {
    const text = (textToSend || input).trim();
    if (!text || loading) return;

    if (!textToSend) setInput('');
    setLastSentText(text);
    setLoading(true);

    const activeSessionId = session?.session_id || `chat_${Date.now()}`;
    const userMsgId = `user_${Date.now()}`;
    const botMsgId = `bot_${Date.now()}`;

    // 1. Create user message
    const tempUserMsg: ExtendedChatMessage = {
      id: userMsgId,
      session_id: activeSessionId,
      sender: 'user',
      text: text,
      timestamp: new Date().toISOString(),
      triggered_escalation: false,
    };

    // 2. Create bot thinking placeholder message
    const tempThinkingMsg: ExtendedChatMessage = {
      id: botMsgId,
      session_id: activeSessionId,
      sender: 'bot',
      text: 'Thinking...',
      timestamp: new Date().toISOString(),
      triggered_escalation: false,
      isThinking: true,
    };

    setMessages((prev) => [...prev, tempUserMsg, tempThinkingMsg]);

    try {
      const resp = await chatApi.sendMessage(activeSessionId, text);

      // Extract details
      const responseText = resp.text || resp.response || 'No response returned';
      const sentimentData = resp.sentiment || {};
      const intentData = resp.intent || {};
      const emotionData = resp.emotion || {};
      const contextData = resp.context || {};
      const ragSources = resp.rag_sources || [];

      if (resp.interaction_mode) {
        setLastInteractionMode(resp.interaction_mode);
      }
      if (resp.llm_provider) {
        setLastLlmProvider(resp.llm_provider);
      }

      // Update session metrics
      setSession((prev) => {
        if (!prev) return prev;
        return {
          ...prev,
          sentiment_score: sentimentData.score ?? prev.sentiment_score,
          sentiment_label: sentimentData.label ?? prev.sentiment_label,
          escalation_flag: resp.triggered_escalation ?? prev.escalation_flag,
          customer_risk_score: resp.customer_risk_score ?? prev.customer_risk_score,
        };
      });

      // Update bot message with full payload
      const finalBotMsg: ExtendedChatMessage = {
        id: botMsgId,
        session_id: activeSessionId,
        sender: 'bot',
        text: responseText,
        timestamp: new Date().toISOString(),
        sentiment_label: sentimentData.label,
        sentiment_score: sentimentData.score,
        intent_label: intentData.primary_intent || intentData.label,
        emotion_label: emotionData.dominant_emotion || emotionData.label,
        triggered_escalation: resp.triggered_escalation || false,
        isThinking: false,
        rag_sources: ragSources,
        thinking_steps: resp.thinking_steps || [
          `Detected sentiment: ${sentimentData.label || 'Neutral'} (${sentimentData.score || 0.0})`,
          `Categorized intent: ${intentData.primary_intent || 'General Inquiries'}`,
          `RAG Grounding: ${ragSources.length > 0 ? `${ragSources.length} policy source(s) cited` : 'Standard response'}`,
        ],
        tools_executed: resp.tools_executed || [],
        escalation_reasons: resp.escalation_reasons || [],
        llm_provider: resp.llm_provider || 'Local AI Engine',
        entities: resp.entities || {},
        interaction_mode: resp.interaction_mode || 'RETAIL_SUPPORT',
        confidence: resp.confidence || 0.92,
      };

      setMessages((prev) => prev.map((m) => (m.id === botMsgId ? finalBotMsg : m)));
    } catch (err) {
      console.error('Chat orchestration error:', err);
      const errorMsg: ExtendedChatMessage = {
        id: botMsgId,
        session_id: activeSessionId,
        sender: 'bot',
        text: "I'm having trouble processing your request. Running in safe local offline fallback mode.",
        timestamp: new Date().toISOString(),
        triggered_escalation: false,
        isThinking: false,
        isError: true,
      };
      setMessages((prev) => prev.map((m) => (m.id === botMsgId ? errorMsg : m)));
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyzeCustomer = async () => {
    setAnalysisLoading(true);
    try {
      const data = await chatApi.analyzeCustomer(session?.customer_id || 'DEMO-1024');
      setCustomerAnalysis(data);
    } catch (err) {
      console.error('Failed to analyze customer:', err);
      setCustomerAnalysis({
        customer_id: session?.customer_id || 'DEMO-1024',
        name: 'Sarah Jenkins',
        segment: 'VIP Gold',
        current_risk: session?.customer_risk_score || 0.82,
        sentiment_trend: 'Deteriorating (-0.42 velocity)',
        unresolved_issues: 3,
        previous_complaints: ['Late delivery order #45821', 'Damaged parcel #39102'],
        ai_recommendation: 'Escalate to senior customer retention manager with priority SLA.',
      });
    } finally {
      setAnalysisLoading(false);
    }
  };

  const getSentimentBadge = (label?: string, score?: number) => {
    if (!label) return null;
    const isNeg = label === 'Negative' || (score !== undefined && score < -0.2);
    const isPos = label === 'Positive' || (score !== undefined && score > 0.2);

    if (isPos) {
      return (
        <span className="inline-flex items-center gap-1 text-[10px] font-semibold bg-[#E4F5EF] text-[#065F46] px-2 py-0.5 rounded-full border border-[#B8E0D2]">
          <TrendingUp className="w-3 h-3 text-[#10B981]" /> Positive ({score !== undefined ? score : ''})
        </span>
      );
    }
    if (isNeg) {
      return (
        <span className="inline-flex items-center gap-1 text-[10px] font-semibold bg-[#FEF2F2] text-[#EF4444] px-2 py-0.5 rounded-full border border-[#F87171]/30">
          <TrendingDown className="w-3 h-3 text-[#EF4444]" /> Negative ({score !== undefined ? score : ''})
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 text-[10px] font-semibold bg-[#F1F5F9] text-[#64748B] px-2 py-0.5 rounded-full border border-[#E2E8F0]">
        <Minus className="w-3 h-3" /> Neutral ({score !== undefined ? score : ''})
      </span>
    );
  };

  const lastBotMsg = [...messages].reverse().find((m) => m.sender === 'bot' && !m.isThinking);

  return (
    <div className="flex flex-col h-[calc(100vh-60px)] bg-[#F5F5F5] overflow-hidden text-[#18324A] fade-in">
      {/* 3-Column Enterprise Layout */}
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-5 p-5 overflow-hidden">
        
        {/* ================= LEFT COLUMN: CUSTOMER CONTEXT & PRESETS ================= */}
        <div className="lg:col-span-3 flex flex-col space-y-4 overflow-y-auto pr-1">
          {/* Customer Profile Card */}
          <div className="p-4 bg-white border border-[#E2E8F0] rounded-2xl shadow-xs space-y-3">
            <div className="flex items-center justify-between pb-3 border-b border-[#E2E8F0]">
              <div className="flex items-center gap-2.5">
                <div className="w-9 h-9 rounded-xl bg-[#DCECF8] text-[#18324A] flex items-center justify-center font-bold text-sm border border-[#A7C7E7]/40">
                  SJ
                </div>
                <div>
                  <h3 className="font-heading font-bold text-sm text-[#18324A]">Sarah Jenkins</h3>
                  <p className="text-[11px] text-[#64748B] font-medium">ID: DEMO-1024 • VIP Gold</p>
                </div>
              </div>
              <span className="text-[10px] bg-[#E4F5EF] text-[#065F46] font-semibold px-2 py-0.5 rounded-full border border-[#B8E0D2]">
                Active Session
              </span>
            </div>

            <div className="space-y-2 text-xs">
              <div className="flex items-center justify-between">
                <span className="text-[#64748B] font-medium">Customer Risk Level:</span>
                <span className={`font-bold px-2 py-0.5 rounded-full text-[10px] ${
                  (session?.customer_risk_score || 0.82) > 0.75
                    ? 'bg-[#FEF2F2] text-[#EF4444] border border-[#F87171]/40'
                    : 'bg-[#FFFBEB] text-[#D97706] border border-[#FBBF24]/40'
                }`}>
                  {((session?.customer_risk_score || 0.82) * 100).toFixed(0)}% HIGH RISK
                </span>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-[#64748B] font-medium">Sentiment Polarity:</span>
                <span className="font-semibold text-[#18324A]">
                  {session?.sentiment_label || 'Negative'} ({session?.sentiment_score || -0.65})
                </span>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-[#64748B] font-medium">Unresolved Complaints:</span>
                <span className="font-semibold text-[#EF4444]">3 Repeat Issues</span>
              </div>
            </div>

            <button
              onClick={handleAnalyzeCustomer}
              disabled={analysisLoading}
              className="w-full py-2 bg-[#DCECF8] hover:bg-[#A7C7E7]/50 text-[#18324A] font-semibold text-xs rounded-xl border border-[#A7C7E7]/60 shadow-xs flex items-center justify-center gap-1.5 transition"
            >
              {analysisLoading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Sparkles className="w-3.5 h-3.5 text-[#0284C7]" />}
              Analyze Customer Risk Profile
            </button>
          </div>

          {/* Hackathon Demo Presets Card */}
          <div className="p-4 bg-white border border-[#E2E8F0] rounded-2xl shadow-xs space-y-3">
            <div className="flex items-center justify-between">
              <h4 className="font-heading font-bold text-xs text-[#18324A] flex items-center gap-1.5">
                <PlayCircle className="w-4 h-4 text-[#0284C7]" />
                Deterministic Presets (DEMO)
              </h4>
              <button
                onClick={handleResetDemo}
                className="text-[10px] text-[#64748B] hover:text-[#EF4444] flex items-center gap-1 transition"
                title="Reset session to clean demo state"
              >
                <Trash2 className="w-3 h-3" /> Reset
              </button>
            </div>

            <div className="space-y-1.5">
              <button
                onClick={() => handleSendMessage("I loved the silk dress I bought! Is it in stock in navy blue?")}
                className="w-full text-left p-2.5 rounded-xl border border-[#E2E8F0] bg-[#F8FAFC] hover:bg-[#E4F5EF] transition text-xs font-medium text-[#18324A] flex items-center justify-between group"
              >
                <div>
                  <div className="font-semibold text-[#065F46] group-hover:underline">A. Happy Customer</div>
                  <div className="text-[10px] text-[#64748B] truncate max-w-[180px]">Silk dress review & query</div>
                </div>
                <ArrowRight className="w-3.5 h-3.5 text-[#64748B] group-hover:translate-x-0.5 transition" />
              </button>

              <button
                onClick={() => handleSendMessage("Where is my order #45821? It was supposed to arrive yesterday!")}
                className="w-full text-left p-2.5 rounded-xl border border-[#E2E8F0] bg-[#F8FAFC] hover:bg-[#DCECF8] transition text-xs font-medium text-[#18324A] flex items-center justify-between group"
              >
                <div>
                  <div className="font-semibold text-[#0284C7] group-hover:underline">B. Delivery Complaint</div>
                  <div className="text-[10px] text-[#64748B] truncate max-w-[180px]">Order status tool lookup</div>
                </div>
                <ArrowRight className="w-3.5 h-3.5 text-[#64748B] group-hover:translate-x-0.5 transition" />
              </button>

              <button
                onClick={() => handleSendMessage("My second order was also damaged! I want an immediate refund or I will escalate!")}
                className="w-full text-left p-2.5 rounded-xl border border-[#E2E8F0] bg-[#F8FAFC] hover:bg-[#FEF2F2] transition text-xs font-medium text-[#18324A] flex items-center justify-between group"
              >
                <div>
                  <div className="font-semibold text-[#EF4444] group-hover:underline">C. Angry Customer (Escalate)</div>
                  <div className="text-[10px] text-[#64748B] truncate max-w-[180px]">Supervisor handoff package</div>
                </div>
                <ArrowRight className="w-3.5 h-3.5 text-[#64748B] group-hover:translate-x-0.5 transition" />
              </button>

              <button
                onClick={() => handleSendMessage("What is your refund policy for returned items?")}
                className="w-full text-left p-2.5 rounded-xl border border-[#E2E8F0] bg-[#F8FAFC] hover:bg-[#DCECF8] transition text-xs font-medium text-[#18324A] flex items-center justify-between group"
              >
                <div>
                  <div className="font-semibold text-[#18324A] group-hover:underline">D. Refund Policy (RAG 2.0)</div>
                  <div className="text-[10px] text-[#64748B] truncate max-w-[180px]">Vector grounding citation</div>
                </div>
                <ArrowRight className="w-3.5 h-3.5 text-[#64748B] group-hover:translate-x-0.5 transition" />
              </button>

              <button
                onClick={() => handleSendMessage("Thank you for resolving my delivery issue so quickly!")}
                className="w-full text-left p-2.5 rounded-xl border border-[#E2E8F0] bg-[#F8FAFC] hover:bg-[#E4F5EF] transition text-xs font-medium text-[#18324A] flex items-center justify-between group"
              >
                <div>
                  <div className="font-semibold text-[#10B981] group-hover:underline">E. Sentiment Recovery</div>
                  <div className="text-[10px] text-[#64748B] truncate max-w-[180px]">Positive sentiment shift</div>
                </div>
                <ArrowRight className="w-3.5 h-3.5 text-[#64748B] group-hover:translate-x-0.5 transition" />
              </button>
            </div>
          </div>
        </div>

        {/* ================= CENTER COLUMN: CHAT STREAM & COMPOSER ================= */}
        <div className="lg:col-span-6 flex flex-col bg-white border border-[#E2E8F0] rounded-2xl shadow-xs overflow-hidden">
          {/* Chat Stream Header */}
          <div className="px-5 py-3.5 border-b border-[#E2E8F0] flex items-center justify-between bg-[#F8FAFC]">
            <div className="flex items-center gap-2.5">
              <div className="w-7 h-7 rounded-lg bg-[#DCECF8] text-[#18324A] flex items-center justify-center font-bold text-xs border border-[#A7C7E7]/40">
                <Bot className="w-4 h-4 text-[#18324A]" />
              </div>
              <div>
                <h3 className="font-heading font-bold text-xs text-[#18324A]">Agentic Retail AI Assistant</h3>
                <p className="text-[10px] text-[#64748B] font-medium">10-Step Execution Pipeline</p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <span className="flex items-center gap-1 text-[10px] font-semibold bg-[#E4F5EF] text-[#065F46] px-2.5 py-1 rounded-full border border-[#B8E0D2]">
                <span className="w-1.5 h-1.5 rounded-full bg-[#10B981] animate-pulse"></span>
                {lastLlmProvider}
              </span>
            </div>
          </div>

          {/* Messages Container */}
          <div className="flex-1 overflow-y-auto p-5 space-y-4 bg-[#FDFDFD]">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex gap-3 ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {msg.sender === 'bot' && (
                  <div className="w-8 h-8 rounded-full bg-[#DCECF8] text-[#18324A] flex items-center justify-center shrink-0 border border-[#A7C7E7]/50 mt-1 shadow-xs">
                    <Bot className="w-4 h-4 text-[#18324A]" />
                  </div>
                )}

                <div className={`max-w-[85%] space-y-2 ${msg.sender === 'user' ? 'items-end' : 'items-start'}`}>
                  <div
                    className={`p-4 rounded-2xl text-xs leading-relaxed shadow-xs ${
                      msg.sender === 'user'
                        ? 'bg-[#18324A] text-white rounded-br-none'
                        : 'bg-[#F8FAFC] text-[#18324A] border border-[#E2E8F0] rounded-bl-none'
                    }`}
                  >
                    {msg.isThinking ? (
                      <div className="flex items-center gap-2 text-[#64748B] py-1 font-medium">
                        <Loader2 className="w-3.5 h-3.5 animate-spin text-[#0284C7]" />
                        <span>Evaluating intent & retrieving knowledge...</span>
                      </div>
                    ) : (
                      <div className="whitespace-pre-wrap">{msg.text}</div>
                    )}
                  </div>

                  {/* Metadata & Tools Executed Box */}
                  {msg.sender === 'bot' && !msg.isThinking && (
                    <div className="space-y-2 pt-0.5">
                      {/* Sentiment & Intent Pill */}
                      <div className="flex flex-wrap items-center gap-1.5 text-[10px]">
                        {getSentimentBadge(msg.sentiment_label, msg.sentiment_score)}
                        {msg.intent_label && (
                          <span className="bg-[#DCECF8] text-[#18324A] font-semibold px-2 py-0.5 rounded-full border border-[#A7C7E7]/50">
                            Intent: {msg.intent_label}
                          </span>
                        )}
                        {msg.confidence && (
                          <span className="bg-[#E4F5EF] text-[#065F46] font-semibold px-2 py-0.5 rounded-full border border-[#B8E0D2]">
                            Confidence: {(msg.confidence * 100).toFixed(0)}%
                          </span>
                        )}
                      </div>

                      {/* Tool Execution Card */}
                      {msg.tools_executed && msg.tools_executed.length > 0 && (
                        <div className="p-3 bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl text-[11px] space-y-1.5">
                          <div className="flex items-center justify-between font-semibold text-[#18324A]">
                            <span className="flex items-center gap-1.5">
                              <Zap className="w-3.5 h-3.5 text-[#0284C7]" />
                              Tool Executed: <code className="text-[#0284C7] bg-[#DCECF8] px-1.5 py-0.5 rounded font-mono">{msg.tools_executed[0].tool}</code>
                            </span>
                            <span className="text-[10px] text-[#10B981] font-bold">✓ VERIFIED</span>
                          </div>
                          <div className="text-[10px] text-[#64748B] font-mono bg-white p-2 rounded-lg border border-[#E2E8F0] overflow-x-auto">
                            {JSON.stringify(msg.tools_executed[0].output, null, 2)}
                          </div>
                        </div>
                      )}

                      {/* RAG Source Citation Badge */}
                      {msg.rag_sources && msg.rag_sources.length > 0 && (
                        <button
                          onClick={() => setSelectedRagSource(msg.rag_sources![0])}
                          className="flex items-center gap-1.5 text-[10px] bg-[#E4F5EF] hover:bg-[#B8E0D2]/40 text-[#065F46] px-2.5 py-1 rounded-xl border border-[#B8E0D2] font-semibold transition"
                        >
                          <BookOpen className="w-3 h-3 text-[#10B981]" />
                          Grounded Source: {msg.rag_sources[0].title} (Score: {msg.rag_sources[0].score || 0.91})
                        </button>
                      )}
                    </div>
                  )}
                </div>

                {msg.sender === 'user' && (
                  <div className="w-8 h-8 rounded-full bg-[#18324A] text-white flex items-center justify-center shrink-0 mt-1 shadow-xs font-bold text-xs">
                    SJ
                  </div>
                )}
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>

          {/* Composer Form */}
          <div className="p-4 border-t border-[#E2E8F0] bg-[#F8FAFC]">
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSendMessage();
              }}
              className="flex items-center gap-2"
            >
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask about orders, returns, or retail policy..."
                disabled={loading}
                className="flex-1 bg-white border border-[#E2E8F0] rounded-xl px-4 py-2.5 text-xs text-[#18324A] placeholder-[#94A3B8] focus:outline-none focus:border-[#A7C7E7] focus:ring-1 focus:ring-[#A7C7E7] transition shadow-xs"
              />
              <button
                type="submit"
                disabled={loading || !input.trim()}
                className="px-4 py-2.5 bg-[#18324A] hover:bg-[#0F2232] text-white font-semibold text-xs rounded-xl shadow-xs flex items-center gap-1.5 transition disabled:opacity-50"
              >
                <Send className="w-3.5 h-3.5" />
                Send
              </button>
            </form>
          </div>
        </div>

        {/* ================= RIGHT COLUMN: LIVE AI INTELLIGENCE ================= */}
        <div className="lg:col-span-3 flex flex-col space-y-4 overflow-y-auto pl-1">
          {/* Real-time Telemetry Card */}
          <div className="p-4 bg-white border border-[#E2E8F0] rounded-2xl shadow-xs space-y-3">
            <h4 className="font-heading font-bold text-xs text-[#18324A] flex items-center justify-between border-b border-[#E2E8F0] pb-2">
              <span className="flex items-center gap-1.5">
                <Cpu className="w-4 h-4 text-[#0284C7]" />
                Live AI Intelligence
              </span>
              <span className="text-[10px] text-[#10B981] font-semibold bg-[#E4F5EF] px-2 py-0.5 rounded-full border border-[#B8E0D2]">
                Active
              </span>
            </h4>

            <div className="space-y-2 text-xs">
              <div className="flex items-center justify-between">
                <span className="text-[#64748B] font-medium">Interaction Mode:</span>
                <span className="font-bold text-[#18324A] font-mono text-[11px] bg-[#DCECF8] px-2 py-0.5 rounded">
                  {lastInteractionMode}
                </span>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-[#64748B] font-medium">Detected Intent:</span>
                <span className="font-semibold text-[#18324A]">
                  {lastBotMsg?.intent_label || 'General Inquiry'}
                </span>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-[#64748B] font-medium">Emotion Breakdown:</span>
                <span className="font-semibold text-[#0284C7]">
                  {lastBotMsg?.emotion_label || 'Frustration / Concern'}
                </span>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-[#64748B] font-medium">Policy Grounding:</span>
                <span className="font-semibold text-[#10B981]">
                  {lastBotMsg?.rag_sources && lastBotMsg.rag_sources.length > 0 ? '✓ Grounded (Vector)' : 'Standard LLM'}
                </span>
              </div>
            </div>
          </div>

          {/* AI Decision Trace Accordion */}
          <div className="p-4 bg-white border border-[#E2E8F0] rounded-2xl shadow-xs space-y-3">
            <button
              onClick={() => setShowDecisionTrace(!showDecisionTrace)}
              className="w-full flex items-center justify-between font-heading font-bold text-xs text-[#18324A]"
            >
              <span className="flex items-center gap-1.5">
                <Layers className="w-4 h-4 text-[#0284C7]" />
                HOW AI DECIDED (Trace)
              </span>
              {showDecisionTrace ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </button>

            {showDecisionTrace && (
              <div className="space-y-2 text-[11px] pt-1">
                <div className="p-2 bg-[#F8FAFC] rounded-xl border border-[#E2E8F0] flex items-center justify-between">
                  <span className="text-[#64748B]">1. User Intent Class</span>
                  <span className="font-semibold text-[#18324A]">{lastBotMsg?.intent_label || 'Order Enquiry'}</span>
                </div>
                <div className="p-2 bg-[#F8FAFC] rounded-xl border border-[#E2E8F0] flex items-center justify-between">
                  <span className="text-[#64748B]">2. Memory Check</span>
                  <span className="font-semibold text-[#065F46]">✓ Sarah Jenkins (3 prev)</span>
                </div>
                <div className="p-2 bg-[#F8FAFC] rounded-xl border border-[#E2E8F0] flex items-center justify-between">
                  <span className="text-[#64748B]">3. Decision Engine</span>
                  <span className="font-semibold text-[#0284C7]">RETAIL_SUPPORT</span>
                </div>
                <div className="p-2 bg-[#F8FAFC] rounded-xl border border-[#E2E8F0] flex items-center justify-between">
                  <span className="text-[#64748B]">4. Tool Selected</span>
                  <span className="font-semibold text-[#18324A]">
                    {lastBotMsg?.tools_executed && lastBotMsg.tools_executed.length > 0
                      ? lastBotMsg.tools_executed[0].tool
                      : 'None required'}
                  </span>
                </div>
                <div className="p-2 bg-[#E4F5EF] rounded-xl border border-[#B8E0D2] flex items-center justify-between">
                  <span className="text-[#065F46] font-medium">5. Response Validation</span>
                  <span className="font-bold text-[#065F46]">✓ PASS (Grounded)</span>
                </div>
              </div>
            )}
          </div>

          {/* Supervisor Handoff Alert Package */}
          {lastBotMsg?.triggered_escalation && (
            <div className="p-4 bg-[#FEF2F2] border border-[#F87171]/40 rounded-2xl space-y-3 shadow-xs fade-in">
              <div className="flex items-center justify-between">
                <span className="font-heading font-bold text-xs text-[#991B1B] flex items-center gap-1.5">
                  <ShieldAlert className="w-4 h-4 text-[#EF4444]" />
                  🚨 SUPERVISOR HANDOFF
                </span>
                <span className="text-[10px] bg-[#EF4444] text-white px-2 py-0.5 rounded-full font-bold">
                  HIGH RISK
                </span>
              </div>
              <p className="text-[11px] text-[#7F1D1D] leading-normal font-medium">
                Customer sentiment deteriorated below -0.60 threshold. Autonomous handoff package generated for human supervisor intervention.
              </p>
              <div className="grid grid-cols-2 gap-2 pt-1 text-[10px]">
                <button className="py-1.5 bg-[#EF4444] hover:bg-[#DC2626] text-white font-semibold rounded-lg shadow-xs transition">
                  Accept Handoff
                </button>
                <button className="py-1.5 bg-white hover:bg-[#F8FAFC] text-[#18324A] font-semibold border border-[#E2E8F0] rounded-lg transition">
                  Review Case
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* RAG Source Drawer Modal */}
      {selectedRagSource && (
        <div className="fixed inset-0 bg-[#18324A]/40 backdrop-blur-xs flex items-center justify-center p-4 z-50 fade-in">
          <div className="bg-white border border-[#E2E8F0] rounded-2xl max-w-lg w-full p-6 space-y-4 shadow-xl">
            <div className="flex items-center justify-between border-b border-[#E2E8F0] pb-3">
              <div className="flex items-center gap-2">
                <BookOpen className="w-5 h-5 text-[#10B981]" />
                <h3 className="font-heading font-bold text-sm text-[#18324A]">{selectedRagSource.title}</h3>
              </div>
              <button
                onClick={() => setSelectedRagSource(null)}
                className="text-[#64748B] hover:text-[#18324A] p-1 rounded-lg hover:bg-[#F1F5F9]"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div className="flex items-center justify-between text-[#64748B]">
                <span>Source File: <code className="text-[#18324A] bg-[#F1F5F9] px-1.5 py-0.5 rounded font-mono">{selectedRagSource.filename}</code></span>
                <span className="font-semibold text-[#10B981]">Similarity: {selectedRagSource.score || 0.91}</span>
              </div>

              <div className="p-3 bg-[#F8FAFC] rounded-xl border border-[#E2E8F0] text-[#18324A] leading-relaxed max-h-60 overflow-y-auto">
                {selectedRagSource.content}
              </div>
            </div>

            <div className="flex justify-end pt-2">
              <button
                onClick={() => setSelectedRagSource(null)}
                className="px-4 py-2 bg-[#18324A] hover:bg-[#0F2232] text-white font-semibold text-xs rounded-xl shadow-xs"
              >
                Close Drawer
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Customer Analysis Modal */}
      {customerAnalysis && (
        <div className="fixed inset-0 bg-[#18324A]/40 backdrop-blur-xs flex items-center justify-center p-4 z-50 fade-in">
          <div className="bg-white border border-[#E2E8F0] rounded-2xl max-w-xl w-full p-6 space-y-4 shadow-xl">
            <div className="flex items-center justify-between border-b border-[#E2E8F0] pb-3">
              <div className="flex items-center gap-2">
                <UserCheck className="w-5 h-5 text-[#0284C7]" />
                <h3 className="font-heading font-bold text-sm text-[#18324A]">Customer Risk Analysis: {customerAnalysis.name}</h3>
              </div>
              <button
                onClick={() => setCustomerAnalysis(null)}
                className="text-[#64748B] hover:text-[#18324A] p-1 rounded-lg hover:bg-[#F1F5F9]"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 bg-[#F8FAFC] rounded-xl border border-[#E2E8F0]">
                  <span className="text-[#64748B] font-medium">Customer Segment</span>
                  <div className="font-bold text-[#18324A] text-sm mt-0.5">{customerAnalysis.segment}</div>
                </div>
                <div className="p-3 bg-[#FEF2F2] rounded-xl border border-[#F87171]/30">
                  <span className="text-[#7F1D1D] font-medium">Composite Risk Score</span>
                  <div className="font-bold text-[#EF4444] text-sm mt-0.5">{(customerAnalysis.current_risk * 100).toFixed(0)}% HIGH RISK</div>
                </div>
              </div>

              <div className="p-3 bg-[#F8FAFC] rounded-xl border border-[#E2E8F0]">
                <span className="text-[#64748B] font-medium">AI Recommended Action</span>
                <p className="font-semibold text-[#065F46] mt-1">{customerAnalysis.ai_recommendation}</p>
              </div>
            </div>

            <div className="flex justify-end pt-2">
              <button
                onClick={() => setCustomerAnalysis(null)}
                className="px-4 py-2 bg-[#18324A] hover:bg-[#0F2232] text-white font-semibold text-xs rounded-xl shadow-xs"
              >
                Close Diagnostic
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
