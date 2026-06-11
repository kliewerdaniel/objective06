import React from 'react';
import { cn } from '../utils/cn';

export interface AlertProps {
  children: React.ReactNode;
  variant?: 'info' | 'success' | 'warning' | 'danger';
  className?: string;
  onDismiss?: () => void;
}

export function Alert({ children, variant = 'info', className, onDismiss }: AlertProps) {
  return (
    <div className={cn('self-alert', `self-alert--${variant}`, className)} role="alert">
      <span className="self-alert__content">{children}</span>
      {onDismiss && <button className="self-alert__dismiss" onClick={onDismiss} aria-label="Dismiss">&times;</button>}
    </div>
  );
}
