type ClassValue = string | number | boolean | null | undefined | ClassValue[] | Record<string, boolean | null | undefined>;

export function cn(...args: ClassValue[]): string {
  const classes: string[] = [];
  for (const arg of args) {
    if (!arg) continue;
    if (typeof arg === 'string') {
      classes.push(arg);
    } else if (Array.isArray(arg)) {
      classes.push(cn(...arg));
    } else if (typeof arg === 'object') {
      for (const [key, value] of Object.entries(arg)) {
        if (value) classes.push(key);
      }
    }
  }
  return classes.join(' ');
}
