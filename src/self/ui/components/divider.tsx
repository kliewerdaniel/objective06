import React from 'react';
import { cn } from '../utils/cn';

export interface DividerProps {
  orientation?: 'horizontal' | 'vertical';
  className?: string;
  label?: string;
}

export function Divider({ orientation = 'horizontal', className, label }: DividerProps) {
  return (
    <div className={cn('self-divider', `self-divider--${orientation}`, label && 'self-divider--with-label', className)} role="separator">
      {label && <span className="self-divider__label">{label}</span>}
    </div>
  );
}
