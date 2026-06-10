import React from 'react';
import { cn } from '../utils/cn';

export interface DropdownOption {
  label: string;
  value: string | number;
  disabled?: boolean;
  disabledReason?: string;
}

export interface DropdownProps {
  label: string;
  options: DropdownOption[];
  value: string | number;
  onChange: (value: string | number, option: DropdownOption) => void;
  className?: string;
  multiSelect?: boolean;
}

export function Dropdown({
  label,
  options,
  value,
  onChange,
  className,
  multiSelect = false,
}: DropdownProps) {
  return (
    <div className={cn('self-dropdown', className)}>
      <label className="self-dropdown__label">{label}</label>
      <select
        className="self-dropdown__select"
        multiple={multiSelect}
        value={value}
        onChange={(e) => {
          const selected = e.target.selectedOptions;
          if (selected.length > 0) {
            onChange(selected[0].value, selected[0]);
          }
        }}
      >
        {options.map((option) => (
          <option key={option.value} value={option.value} disabled={option.disabled}>
            {option.label}
          </option>
        ))}
      </select>
    </div>
  );
}
