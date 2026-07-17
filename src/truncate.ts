/**
 * Shorten text to a maximum display length.
 *
 * - Returns `text` unchanged when it already fits within `maxLength`.
 * - Otherwise cuts `text` so the result, including `suffix`, is exactly
 *   `maxLength` characters long.
 * - Edge case: when `maxLength` is shorter than `suffix.length` there is no
 *   room to append any original text alongside the suffix, so the suffix
 *   itself is sliced down to `maxLength` and returned (e.g.
 *   `truncate("hello", 2, "...")` returns `".."`).
 */
export function truncate(
  text: string,
  maxLength: number,
  suffix = "...",
): string {
  if (text.length <= maxLength) {
    return text;
  }

  if (maxLength <= suffix.length) {
    return suffix.slice(0, maxLength);
  }

  return text.slice(0, maxLength - suffix.length) + suffix;
}
