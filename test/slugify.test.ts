import { describe, it, expect } from "vitest";
import { slugify } from "../src/slugify.js";

describe("slugify", () => {
  it("lowercases and hyphenates simple text", () => {
    expect(slugify("Hello World")).toBe("hello-world");
  });

  it("collapses runs of non-alphanumeric characters into one hyphen", () => {
    expect(slugify("Foo -- Bar__Baz!!!")).toBe("foo-bar-baz");
  });

  it("trims leading and trailing separators", () => {
    expect(slugify("  ...Edge Case!  ")).toBe("edge-case");
  });

  it("returns an empty string when there is nothing usable", () => {
    expect(slugify("!!!")).toBe("");
  });
});
