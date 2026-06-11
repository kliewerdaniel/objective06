import React from 'react';
import { cn } from '../utils/cn';

export interface ChartSeries {
  name: string;
  data: number[];
  color?: string;
}

export interface ChartProps {
  type: 'line' | 'bar' | 'area';
  series: ChartSeries[];
  labels?: string[];
  height?: number;
  className?: string;
}

export function Chart({ type, series, labels, height = 300, className }: ChartProps) {
  return (
    <div className={cn('self-chart', `self-chart--${type}`, className)} style={{ height }}>
      <div className="self-chart__placeholder">
        <p>Chart visualization (${type}) — requires a charting library integration</p>
        {series.length > 0 && (
          <ul className="self-chart__series">
            {series.map(s => (
              <li key={s.name}>{s.name}: [{s.data.join(', ')}]</li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
