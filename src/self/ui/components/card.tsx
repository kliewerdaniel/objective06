import React from 'react';
import { cn } from '../utils/cn';

export interface CardProps {
  children: React.ReactNode;
  className?: string;
  variant?: 'default' | 'elevated' | 'outlined';
  padding?: 'none' | 'sm' | 'md' | 'lg';
}

export function Card({ children, className, variant = 'default', padding = 'md' }: CardProps) {
  return (
    <div className={cn('self-card', `self-card--${variant}`, `self-card--padding-${padding}`, className)}>
      {children}
    </div>
  );
}
