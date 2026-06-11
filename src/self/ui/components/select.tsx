import React from 'react';
import { cn } from '../utils/cn';

export interface SelectOption {
  value: string;
  label: string;
}

export interface SelectProps {
  options: SelectOption[];
  value?: string;
  onChange?: (value: string) => void;
  placeholder?: string;
  label?: string;
  error?: string;
  className?: string;
}

export function Select({ options, value, onChange, placeholder, label, error, className }: SelectProps) {
  return (
    <div className={cn('self-select-wrapper', className)}>
      {label && <label className="self-select__label">{label}</label>}
      <select className={cn('self-select', error && 'self-select--error')} value={value ?? ''} onChange={e => onChange?.(e.target.value)}>
        {placeholder && <option value="">{placeholder}</option>}
        {options.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
      </select>
      {error && <span className="self-select__error">{error}</span>}
    </div>
  );
}
