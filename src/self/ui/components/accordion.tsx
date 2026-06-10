import React, { useState } from 'react';
import { cn } from '../utils/cn';

export interface AccordionItem {
  title: string;
  content: React.ReactNode;
  disabled?: boolean;
}

export interface AccordionProps {
  items: AccordionItem[];
  className?: string;
  allowMultiple?: boolean;
}

export function Accordion({ items, className, allowMultiple = false }: AccordionProps) {
  const [openIndex, setOpenIndex] = useState<number | null>(0);

  const toggle = (index: number) => {
    if (allowMultiple) {
      setOpenIndex((prev) => (prev === index ? null : index));
    } else {
      setOpenIndex(openIndex === index ? null : index);
    }
  };

  return (
    <div className={cn('self-accordion', className)}>
      {items.map((item, index) => (
        <div key={item.title} className="self-accordion__item">
          <button
            className={cn('self-accordion__button', openIndex === index && 'self-accordion__button--active')}
            onClick={() => toggle(index)}
            disabled={item.disabled}
          >
            <span>{item.title}</span>
            <span className="self-accordion__icon">
              {openIndex === index ? '▾' : '▸'}
            </span>
          </button>
          {openIndex === index && (
            <div className="self-accordion__panel">
              <div className="self-accordion__content">{item.content}</div>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}