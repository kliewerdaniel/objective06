import React from 'react';
import { cn } from '../utils/cn';

export interface EmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  description?: string;
  action?: React.ReactNode;
  className?: string;
}

export function EmptyState({ icon, title, description, action, className }: EmptyStateProps) {
  return (
    <div className={cn('self-empty-state', className)}>
      {icon && <div className="self-empty-state__icon">{icon}</div>}
      <h3 className="self-empty-state__title">{title}</h3>
      {description && <p className="self-empty-state__description">{description}</p>}
      {action && <div className="self-empty-state__action">{action}</div>}
    </div>
  );
}
