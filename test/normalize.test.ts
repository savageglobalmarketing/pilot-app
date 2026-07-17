import { describe, it, expect } from "vitest";
import { normalize } from "../src/normalize.js";

describe("normalize", () => {
  it("lowercases text", () => {
    expect(normalize("Hello World")).toBe("hello world");
  });

  it("trims surrounding whitespace", () => {
    expect(normalize("  Hello World  ")).toBe("hello world");
  });

  it("lowercases and trims together", () => {
    expect(normalize("  Foo BAR Baz  ")).toBe("foo bar baz");
  });

  it("returns an empty string unchanged", () => {
    expect(normalize("")).toBe("");
  });

  it("returns an empty string when input is only whitespace", () => {
    expect(normalize("   ")).toBe("");
  });

  it("leaves already-normalized text unchanged", () => {
    expect(normalize("already normalized")).toBe("already normalized");
  });
});
