import React from 'react';
import { cn } from '../utils/cn';

export interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
}

export function Textarea({ className, label, error, id, ...props }: TextareaProps) {
  return (
    <div className={cn('self-textarea-wrapper', className)}>
      {label && <label htmlFor={id} className="self-textarea__label">{label}</label>}
      <textarea className={cn('self-textarea', error && 'self-textarea--error')} id={id} {...props} />
      {error && <span className="self-textarea__error">{error}</span>}
    </div>
  );
}
