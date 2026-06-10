import React from 'react';
import { cn } from '../utils/cn';

export interface ToastProps {
  message: React.ReactNode;
  type?: 'info' | 'success' | 'warning' | 'error';
  action?: React.ReactNode;
  onClose?: () => void;
}

export function Toast({ message, type = 'info', action, onClose }: ToastProps) {
  return (
    <div className={cn('self-toast', `self-toast--${type}`)}>
      <span className="self-toast__message">{message}</span>
      {action ? <span className="self-toast__action">{action}</span> : null}
      {onClose ? <button className="self-toast__close" onClick={onClose}>×</button> : null}
    </div>
  );
}
