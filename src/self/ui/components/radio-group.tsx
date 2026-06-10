import React from 'react';
import { cn } from '../utils/cn';

export interface RadioGroupProps {
  options: { value: string; label: string }[];
  value: string;
  onChange: (value: string) => void;
  className?: string;
}

export function RadioGroup({ options, value, onChange, className }: RadioGroupProps) {
  return (
    <div className={cn('self-radio-group', className)}>
      {options.map((opt) => (
        <label key={opt.value} className="self-radio">
          <input
            type="radio"
            name="radio-group"
            value={opt.value}
            checked={value === opt.value}
            onChange={() => onChange(opt.value)}
          />
          <span className="self-radio__mark" />
          {opt.label}
        </label>
      ))}
    </div>
  );
}