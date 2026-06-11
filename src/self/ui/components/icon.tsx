import React from 'react';
import { cn } from '../utils/cn';

export interface IconProps {
  name: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
}

export function Icon({ name, size = 'md', className }: IconProps) {
  return <span className={cn('self-icon', `self-icon--${size}`, `self-icon--${name}`, className)} aria-hidden="true" />;
}
