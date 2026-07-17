/**
 * Constrain a number to an inclusive range [min, max].
 *
 * Returns `min` if `value` is below `min`, `max` if `value` is above `max`,
 * otherwise returns `value` unchanged.
 *
 * @throws {Error} if `min` is greater than `max`.
 */
export function clamp(value: number, min: number, max: number): number {
  if (min > max) {
    throw new Error(`clamp: min (${min}) must not be greater than max (${max})`);
  }

  if (value < min) {
    return min;
  }

  if (value > max) {
    return max;
  }

  return value;
}
