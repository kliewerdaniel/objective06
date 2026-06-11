import React from 'react';
import { cn } from '../utils/cn';

export interface BreadcrumbItem {
  label: string;
  href?: string;
}

export interface BreadcrumbProps {
  items: BreadcrumbItem[];
  className?: string;
}

export function Breadcrumb({ items, className }: BreadcrumbProps) {
  return (
    <nav className={cn('self-breadcrumb', className)} aria-label="Breadcrumb">
      {items.map((item, idx) => (
        <span key={idx} className="self-breadcrumb__item">
          {item.href ? <a href={item.href} className="self-breadcrumb__link">{item.label}</a> : <span className="self-breadcrumb__current">{item.label}</span>}
          {idx < items.length - 1 && <span className="self-breadcrumb__separator" aria-hidden="true">/</span>}
        </span>
      ))}
    </nav>
  );
}
