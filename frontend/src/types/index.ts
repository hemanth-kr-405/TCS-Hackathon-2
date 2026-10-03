export type SentimentType = 'Positive' | 'Neutral' | 'Negative';
export type EmotionType = 'Joy' | 'Satisfaction' | 'Frustration' | 'Anger' | 'Disappointment' | 'Neutral';

export type ViewTab =
  | 'dashboard'
  | 'chatbot'
  | 'dataset'
  | 'aiops'
  | 'feedback'
  | 'analytics'
  | 'intent'
  | 'issues'
  | 'escalations'
  | 'recommendations'
  | 'history'
  | 'modeleval'
  | 'settings';

export interface SentimentAnalysisResult {
  text: string;
  sentiment: SentimentType;
  sentiment_score: number;
  confidence: number;
  intent: string;
  emotion: EmotionType;
  aspect: string;
  probabilities: Record<SentimentType, number>;
}

export interface FeedbackItem {
  id: number;
  customer_id: string;
  text: string;
  source: string;
  category: string;
  product?: string;
  rating?: number;
  sentiment: SentimentType;
  sentiment_score: number;
  confidence: number;
  intent: string;
  emotion: EmotionType;
  aspect: string;
  created_at: string;
}

export interface ChatMessage {
  id: number | string;
  session_id: string;
  sender: 'user' | 'bot';
  text: string;
  sentiment?: SentimentType;
  sentiment_score?: number;
  sentiment_label?: string;
  intent?: string;
  intent_label?: string;
  emotion?: EmotionType;
  emotion_label?: string;
  empathetic_response?: string;
  triggered_escalation: boolean;
  timestamp: string;
  interaction_mode?: string;
}

export interface ChatSession {
  session_id: string;
  customer_id: string;
  customer_name: string;
  status: string;
  conversation_state: string;
  initial_sentiment: SentimentType;
  current_sentiment: SentimentType;
  sentiment_label?: string;
  sentiment_score: number;
  sentiment_trend: string;
  is_escalated: boolean;
  escalation_flag?: boolean;
  customer_risk_score?: number;
  assigned_agent?: string;
  created_at: string;
  updated_at: string;
  messages: ChatMessage[];
}

export interface RecurringIssue {
  id: number;
  issue_key: string;
  title: string;
  category: string;
  description: string;
  frequency: number;
  severity: 'Critical' | 'High' | 'Medium' | 'Low';
  average_sentiment: number;
  status: string;
  created_at: string;
}

export interface BusinessRecommendation {
  id: number;
  recommendation_key: string;
  title: string;
  category: string;
  description: string;
  priority: 'Critical' | 'High' | 'Medium' | 'Low';
  estimated_impact: string;
  status: string;
  created_at: string;
}

export interface EscalationItem {
  id: number;
  session_id: string;
  customer_name: string;
  severity: string;
  reason: string;
  sentiment_score: number;
  status: string;
  assigned_agent: string;
  created_at: string;
}

export interface AnalyticsOverview {
  total_feedback: number;
  positive_count: number;
  neutral_count: number;
  negative_count: number;
  average_sentiment_score: number;
  csat_percentage: number;
  active_escalations: number;
  resolved_issues: number;
  sentiment_distribution: Record<string, number>;
  intent_distribution: Record<string, number>;
  emotion_distribution: Record<string, number>;
  category_sentiment: Record<string, Record<string, number>>;
  recent_feedback: FeedbackItem[];
  top_recurring_issues: RecurringIssue[];
  recommendations: BusinessRecommendation[];
}

export interface ModelMetrics {
  loaded: boolean;
  model_name: string;
  version: string;
  trained_at: string;
  training_samples: number;
  test_samples: number;
  sentiment_accuracy: number;
  sentiment?: {
    accuracy: number;
    precision_macro: number;
    recall_macro: number;
    f1_macro: number;
    confusion_matrix: number[][];
    labels: string[];
  };
}
