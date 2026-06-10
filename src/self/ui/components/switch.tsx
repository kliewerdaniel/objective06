import React from 'react';
import { cn } from '../utils/cn';

export interface SwitchProps {
  label?: string;
  checked: boolean;
  onChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
  className?: string;
}

export function Switch({ label, checked, onChange, className }: SwitchProps) {
  return (
    <div className={cn('self-switch', className)}>
      <input
        type="checkbox"
        checked={checked}
        onChange={onChange}
      />
      <span className="self-switch-track"/>
      <span className="self-switch-handle"/>
      {label ? <span className="self-switch-label">{label}</span> : null}
    </div>
  );
}