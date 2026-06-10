import React from 'react';
import { cn } from '../utils/cn';

export interface TableProps {
  data: Record<string, unknown>[];
  columns: { key: string; header: string; render?: (value: unknown) => React.ReactNode }[];
  className?: string;
  emptyMessage?: string;
}

export function Table({ data, columns, className, emptyMessage = 'No data' }: TableProps) {
  return (
    <table className={cn('self-table', className)}>
      <thead>
        <tr>
          {columns.map((col) => (
            <th key={col.key}>{col.header}</th>
          ))}
        </tr>
      </thead>
      <tbody>
        {data.length === 0 ? (
          <tr>
            <td colSpan={columns.length} className="self-table__empty">
              {emptyMessage}
            </td>
          </tr>
        ) : (
          data.map((row, idx) => (
            <tr key={idx}>
              {columns.map((col) => (
                <td key={col.key}>
                  {col.render ? col.render(row[col.key]) : String(row[col.key] ?? '')}
                </td>
              ))}
            </tr>
          ))
        )}
      </tbody>
    </table>
  );
}