import React from 'react';
import { cn } from '../utils/cn';

export interface BadgeProps {
  children: React.ReactNode;
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'info';
  className?: string;
}

export function Badge({ children, variant = 'default', className }: BadgeProps) {
  return (
    <span className={cn('self-badge', `self-badge--${variant}`, className)}>
      {children}
    </span>
  );
}
