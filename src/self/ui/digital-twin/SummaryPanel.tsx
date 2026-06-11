import React from 'react';
import { Card } from '../components/card';
import { Badge } from '../components/badge';
import { cn } from '../utils/cn';

interface Summary {
  id: string;
  type: 'daily' | 'weekly' | 'topic' | 'project';
  title: string;
  content: string;
  timestamp: string;
  coverage: number;
}

interface SummaryPanelProps {
  summaries: Summary[];
  onSelectSummary?: (summary: Summary) => void;
}

const summaryTypeLabels: Record<string, string> = {
  daily: 'Daily',
  weekly: 'Weekly',
  topic: 'Topic',
  project: 'Project',
};

export function SummaryPanel({ summaries, onSelectSummary }: SummaryPanelProps) {
  return (
    <Card variant="outlined" className="self-summary-panel">
      <h3 className="self-summary-panel__title">Synthesis History</h3>
      <div className="self-summary-panel__list">
        {summaries.length === 0 && (
          <p className="self-summary-panel__empty">No summaries yet. They will appear after synthesis runs.</p>
        )}
        {summaries.map(s => (
          <div
            key={s.id}
            className={cn('self-summary-panel__item')}
            onClick={() => onSelectSummary?.(s)}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => e.key === 'Enter' && onSelectSummary?.(s)}
          >
            <div className="self-summary-panel__item-header">
              <Badge variant="primary">{summaryTypeLabels[s.type]}</Badge>
              <span className="self-summary-panel__item-date">{new Date(s.timestamp).toLocaleDateString()}</span>
            </div>
            <div className="self-summary-panel__item-title">{s.title}</div>
            <div className="self-summary-panel__item-coverage">Coverage: {(s.coverage * 100).toFixed(0)}%</div>
          </div>
        ))}
      </div>
    </Card>
  );
}
