/**
 * Sum a list of numbers. Returns 0 for an empty list.
 */
export function sum(numbers: number[]): number {
  return numbers.reduce((total, n) => total + n, 0);
}

/**
 * Arithmetic mean of a list of numbers. Returns 0 for an empty list.
 */
export function mean(numbers: number[]): number {
  if (numbers.length === 0) {
    return 0;
  }
  return sum(numbers) / numbers.length;
}

/**
 * Median of a list of numbers. Returns 0 for an empty list. For an
 * even-length list, returns the average of the two middle values.
 */
export function median(numbers: number[]): number {
  if (numbers.length === 0) {
    return 0;
  }
  const sorted = [...numbers].sort((a, b) => a - b);
  const mid = Math.floor(sorted.length / 2);
  if (sorted.length % 2 === 0) {
    return (sorted[mid - 1] + sorted[mid]) / 2;
  }
  return sorted[mid];
}
