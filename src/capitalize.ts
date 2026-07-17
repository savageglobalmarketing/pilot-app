/**
 * Capitalize each whitespace-separated word in `text`.
 *
 * - The first letter of every word is upper-cased; the rest of the word is
 *   lower-cased (e.g. `"hELLo wORLD"` -> `"Hello World"`).
 * - Hyphenated words have each hyphen-separated part capitalized on its own
 *   (e.g. `"well-known"` -> `"Well-Known"`, `"mother-in-law"` ->
 *   `"Mother-In-Law"`).
 * - Leading and trailing whitespace is preserved as-is; only the words
 *   themselves are re-cased.
 * - Runs of internal whitespace are preserved (splitting is done on the
 *   whitespace boundaries, not collapsed).
 * - Returns `""` unchanged for an empty string.
 */
export function capitalize(text: string): string {
  if (text === "") {
    return "";
  }

  return text.replace(/\S+/g, (word) => {
    return word
      .split("-")
      .map((part) => part.charAt(0).toUpperCase() + part.slice(1).toLowerCase())
      .join("-");
  });
}
