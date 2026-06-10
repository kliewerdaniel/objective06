import React from 'react';
import { cn } from '../utils/cn';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  fullWidth?: boolean;
}

export function Button({
  children,
  className,
  variant = 'primary',
  size = 'md',
  loading = false,
  fullWidth = false,
  disabled,
  ...props
}: ButtonProps) {
  return (
    <button
      className={cn(
        'self-button',
        `self-button--${variant}`,
        `self-button--${size}`,
        fullWidth && 'self-button--full-width',
        loading && 'self-button--loading',
        className,
      )}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? <span className="self-button__spinner" /> : null}
      {children}
    </button>
  );
}
