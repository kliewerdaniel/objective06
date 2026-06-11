import React from 'react';
import { cn } from '../utils/cn';

export interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export function Spinner({ size = 'md', className }: SpinnerProps) {
  return <span className={cn('self-spinner', `self-spinner--${size}`, className)} aria-label="Loading" />;
}
