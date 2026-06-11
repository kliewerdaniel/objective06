import React, { useState } from 'react';
import { cn } from '../utils/cn';

export interface Tab {
  id: string;
  label: string;
  content: React.ReactNode;
}

export interface TabsProps {
  tabs: Tab[];
  defaultTab?: string;
  className?: string;
}

export function Tabs({ tabs, defaultTab, className }: TabsProps) {
  const [active, setActive] = useState(defaultTab ?? tabs[0]?.id);
  const activeTab = tabs.find(t => t.id === active);

  return (
    <div className={cn('self-tabs', className)}>
      <div className="self-tabs__nav" role="tablist">
        {tabs.map(t => (
          <button key={t.id} role="tab" aria-selected={t.id === active} className={cn('self-tabs__tab', t.id === active && 'self-tabs__tab--active')} onClick={() => setActive(t.id)}>
            {t.label}
          </button>
        ))}
      </div>
      <div className="self-tabs__content" role="tabpanel">
        {activeTab?.content}
      </div>
    </div>
  );
}
