import React from 'react';
import { cn } from '../utils/cn';

export interface ProgressProps {
  value: number;
  status?: 'active' | 'success' | 'error' | 'warning';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export function Progress({ value, status = 'active', size = 'md', className }: ProgressProps) {
  return (
    <div className={cn('self-progress', `self-progress--${size}`, `self-progress--${status}`, className)}>
      <div className="self-progress__bar">
        <div className="self-progress__filled" style={{ width: `${Math.min(value, 100)}%` }} />
      </div>
      <span className="self-progress__label">${value}%</span>
    </div>
  );
}