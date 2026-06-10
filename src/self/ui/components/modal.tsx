import React from 'react';
import { cn } from '../utils/cn';

export interface ModalProps {
  children: React.ReactNode;
  open: boolean;
  onClose: () => void;
  title?: React.ReactNode;
  footer?: React.ReactNode;
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'fullscreen';
  closeOnOverlayClick?: boolean;
}

export function Modal({
  children,
  open,
  onClose,
  title,
  footer,
  size = 'md',
  closeOnOverlayClick = true,
}: ModalProps) {
  if (!open) return null;

  return (
    <div className="self-modal-overlay" onClick={closeOnOverlayClick ? onClose : undefined}>
      <div className={cn('self-modal', `self-modal--${size}`)} onClick={(e) => e.stopPropagation()}>
        {title ? <div className="self-modal-header">{title}</div> : null}
        <div className="self-modal-content">{children}</div>
        {footer ? <div className="self-modal-footer">{footer}</div> : null}
      </div>
    </div>
  );
}
