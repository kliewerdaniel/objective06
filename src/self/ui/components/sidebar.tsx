import React from 'react';
import { cn } from '../utils/cn';

export interface SidebarItem {
  id: string;
  label: string;
  icon?: React.ReactNode;
  badge?: string | number;
  onClick?: () => void;
}

export interface SidebarProps {
  items: SidebarItem[];
  activeItem?: string;
  className?: string;
  header?: React.ReactNode;
  footer?: React.ReactNode;
}

export function Sidebar({ items, activeItem, className, header, footer }: SidebarProps) {
  return (
    <aside className={cn('self-sidebar', className)}>
      {header && <div className="self-sidebar__header">{header}</div>}
      <nav className="self-sidebar__nav">
        {items.map(item => (
          <button
            key={item.id}
            className={cn('self-sidebar__item', item.id === activeItem && 'self-sidebar__item--active')}
            onClick={item.onClick}
          >
            {item.icon && <span className="self-sidebar__item-icon">{item.icon}</span>}
            <span className="self-sidebar__item-label">{item.label}</span>
            {item.badge !== undefined && <span className="self-sidebar__item-badge">{item.badge}</span>}
          </button>
        ))}
      </nav>
      {footer && <div className="self-sidebar__footer">{footer}</div>}
    </aside>
  );
}
