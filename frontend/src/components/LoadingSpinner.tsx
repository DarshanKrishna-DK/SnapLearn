type Props = { className?: string };

export function LoadingSpinner({ className = '' }: Props) {
  return (
    <div
      className={`h-8 w-8 animate-spin rounded border-2 border-cream-200/20 border-t-gold-400 ${className}`}
      role="status"
      aria-label="Loading"
    />
  );
}
