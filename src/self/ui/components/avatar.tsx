import React from 'react';
import { cn } from '../utils/cn';

export interface AvatarProps {
  src?: string;
  alt?: string;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export function Avatar({ src, alt = '', size = 'md', className }: AvatarProps) {
  return (
    <img
      src={src}
      alt={alt}
      className={cn('self-avatar', `self-avatar--${size}`, className)}
    />
  );
}
