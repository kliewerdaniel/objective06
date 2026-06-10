import React from 'react';
import { cn } from '../utils/cn';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  prefix?: React.ReactNode;
  suffix?: React.ReactNode;
}

export function Input({
  className,
  label,
  error,
  helperText,
  prefix,
  suffix,
  id,
  ...props
}: InputProps) {
  return (
    <div className={cn('self-input-wrapper', className)}>
      {label ? <label htmlFor={id}>{label}</label> : null}
      <div className="self-input-container">
        {prefix ? <span className="self-input-prefix">{prefix}</span> : null}
        <input className="self-input" id={id} {...props} />
        {suffix ? <span className="self-input-suffix">{suffix}</span> : null}
      </div>
      {error ? <span className="self-input-error">{error}</span> : null}
      {!error && helperText ? <span className="self-input-helper">{helperText}</span> : null}
    </div>
  );
}
