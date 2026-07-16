/**
 * Sum a list of numbers. Returns 0 for an empty list.
 */
export function sum(numbers: number[]): number {
  return numbers.reduce((total, n) => total + n, 0);
}
