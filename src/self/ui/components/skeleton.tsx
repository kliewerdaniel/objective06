import React from 'react';
import { cn } from '../utils/cn';

export interface SkeletonProps {
  variant?: 'text' | 'circular' | 'rectangular';
  width?: string | number;
  height?: string | number;
  className?: string;
}

export function Skeleton({ variant = 'text', width, height, className }: SkeletonProps) {
  return (
    <div
      className={cn('self-skeleton', `self-skeleton--${variant}`, className)}
      style={{ width, height }}
    />
  );
}