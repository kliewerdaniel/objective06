import React from 'react';
import { Card } from '../components/card';
import { Badge } from '../components/badge';
import { Progress } from '../components/progress';

interface SubsystemHealth {
  name: string;
  status: 'healthy' | 'degraded' | 'down';
  uptime: string;
  eventCount: number;
  lastActivity: string;
}

interface MetricCard {
  label: string;
  value: string;
  change?: string;
  trend?: 'up' | 'down' | 'stable';
}

interface SystemDashboardProps {
  subsystems: SubsystemHealth[];
  metrics: MetricCard[];
  personaSimilarity?: number;
  knowledgeCount?: number;
  storageSize?: string;
}

export function SystemDashboard({ subsystems, metrics, personaSimilarity, knowledgeCount, storageSize }: SystemDashboardProps) {
  return (
    <div className="self-dashboard">
      <div className="self-dashboard__metrics">
        {metrics.map(m => (
          <Card key={m.label} variant="elevated" padding="sm" className="self-dashboard__metric-card">
            <div className="self-dashboard__metric-label">{m.label}</div>
            <div className="self-dashboard__metric-value">{m.value}</div>
            {m.change && (
              <div className={`self-dashboard__metric-change self-dashboard__metric-change--${m.trend ?? 'stable'}`}>
                {m.change}
              </div>
            )}
          </Card>
        ))}
      </div>

      {personaSimilarity !== undefined && (
        <Card variant="outlined" className="self-dashboard__persona">
          <h3>Persona Coherence</h3>
          <Progress value={personaSimilarity} max={1} />
          <span>{(personaSimilarity * 100).toFixed(1)}% consistent</span>
        </Card>
      )}

      <Card variant="outlined" className="self-dashboard__subsystems">
        <h3>Subsystem Health</h3>
        <table className="self-table">
          <thead>
            <tr>
              <th>Subsystem</th>
              <th>Status</th>
              <th>Uptime</th>
              <th>Events</th>
              <th>Last Activity</th>
            </tr>
          </thead>
          <tbody>
            {subsystems.map(s => (
              <tr key={s.name}>
                <td>{s.name}</td>
                <td><Badge variant={s.status === 'healthy' ? 'primary' : s.status === 'degraded' ? 'warning' : 'danger'}>{s.status}</Badge></td>
                <td>{s.uptime}</td>
                <td>{s.eventCount.toLocaleString()}</td>
                <td>{s.lastActivity}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>

      <div className="self-dashboard__storage">
        {knowledgeCount !== undefined && (
          <Card variant="outlined" padding="sm">
            <strong>Knowledge Objects</strong>: {knowledgeCount.toLocaleString()}
          </Card>
        )}
        {storageSize && (
          <Card variant="outlined" padding="sm">
            <strong>Storage Used</strong>: {storageSize}
          </Card>
        )}
      </div>
    </div>
  );
}
