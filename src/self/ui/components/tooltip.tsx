import React from 'react';
import { cn } from '../utils/cn';

export interface TooltipProps {
  content: React.ReactNode;
  placement?: 'top' | 'right' | 'bottom' | 'left';
  trigger?: 'hover' | 'click' | 'focus';
  className?: string;
}

export function Tooltip({ content, placement = 'top', trigger = 'hover', className }: TooltipProps) {
  return (
    <div className={cn('self-tooltip-wrapper', className)}>
      {content}
      <div className="self-tooltip">
        <div className={`self-tooltip--${placement}`}>
          {trigger}
        </div>
      </div>
    </div>
  );
}
