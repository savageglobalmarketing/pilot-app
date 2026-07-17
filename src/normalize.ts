/**
 * Normalize text for further processing.
 *
 * - Lowercases the text
 * - Trims surrounding whitespace
 *
 * Internal helper — not part of the public API.
 */
export function normalize(text: string): string {
  return text.toLowerCase().trim();
}
