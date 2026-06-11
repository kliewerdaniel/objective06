import React from 'react';
import { cn } from '../utils/cn';

export interface ErrorBoundaryProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
  className?: string;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback ?? (
        <div className={cn('self-error-boundary', this.props.className)} role="alert">
          <h3>Something went wrong</h3>
          <p>{this.state.error?.message ?? 'An unexpected error occurred.'}</p>
        </div>
      );
    }
    return this.props.children;
  }
}
