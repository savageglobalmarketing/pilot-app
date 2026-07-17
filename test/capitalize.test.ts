import { describe, it, expect } from "vitest";
import { capitalize } from "../src/capitalize.js";

describe("capitalize", () => {
  it("returns an empty string unchanged", () => {
    expect(capitalize("")).toBe("");
  });

  it("capitalizes a single word", () => {
    expect(capitalize("hello")).toBe("Hello");
  });

  it("capitalizes each word in a multi-word string", () => {
    expect(capitalize("hello world")).toBe("Hello World");
  });

  it("lowercases the rest of mixed-case words", () => {
    expect(capitalize("hELLo wORLD")).toBe("Hello World");
  });

  it("preserves leading and trailing spaces", () => {
    expect(capitalize("  hello world  ")).toBe("  Hello World  ");
  });

  it("preserves internal whitespace runs", () => {
    expect(capitalize("hello   world")).toBe("Hello   World");
  });

  it("handles a string that is only whitespace", () => {
    expect(capitalize("   ")).toBe("   ");
  });

  it("handles single-character words", () => {
    expect(capitalize("a b c")).toBe("A B C");
  });

  it("capitalizes each part of a hyphenated word", () => {
    expect(capitalize("well-known")).toBe("Well-Known");
  });

  it("capitalizes each part of a multi-hyphen word", () => {
    expect(capitalize("mother-in-law")).toBe("Mother-In-Law");
  });

  it("lowercases the rest of each hyphenated part when mixed case", () => {
    expect(capitalize("wELL-kNOWN")).toBe("Well-Known");
  });

  it("capitalizes hyphenated words within a multi-word string", () => {
    expect(capitalize("a well-known author")).toBe("A Well-Known Author");
  });
});
