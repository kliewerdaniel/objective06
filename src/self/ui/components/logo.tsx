import React from 'react';
import { cn } from '../utils/cn';

export interface LogoProps {
  variant?: 'full' | 'icon' | 'text';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export function Logo({ variant = 'full', size = 'md', className }: LogoProps) {
  return (
    <div className={cn('self-logo', `self-logo--${variant}`, `self-logo--${size}`, className)}>
      <span className="self-logo__icon" aria-hidden="true">S</span>
      {variant !== 'icon' && <span className="self-logo__text">SELF</span>}
    </div>
  );
}
