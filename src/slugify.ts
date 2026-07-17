import { normalize } from "./normalize.js";

/**
 * Convert arbitrary text into a URL-safe slug.
 *
 * - Lowercases the text
 * - Trims surrounding whitespace
 * - Replaces any run of non-alphanumeric characters with a single hyphen
 * - Strips leading/trailing hyphens
 */
export function slugify(text: string): string {
  return normalize(text)
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}
