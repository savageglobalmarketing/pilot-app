import { describe, it, expect } from "vitest";
import { truncate } from "../src/truncate.js";

describe("truncate", () => {
  it("returns short text unchanged", () => {
    expect(truncate("hello", 10)).toBe("hello");
  });

  it("truncates long text so the result including the suffix fits maxLength", () => {
    expect(truncate("hello world", 8)).toBe("hello...");
    expect(truncate("hello world", 8).length).toBe(8);
  });

  it("returns text unchanged when maxLength equals the text length", () => {
    expect(truncate("hello", 5)).toBe("hello");
  });

  it("slices the suffix itself when maxLength is shorter than the suffix length", () => {
    expect(truncate("hello", 2, "...")).toBe("..");
    expect(truncate("hello", 0, "...")).toBe("");
  });

  it("returns an empty string unchanged", () => {
    expect(truncate("", 5)).toBe("");
  });

  it("supports a custom suffix", () => {
    expect(truncate("hello world", 7, "…")).toBe("hello …");
  });

  it("handles maxLength exactly equal to the suffix length", () => {
    expect(truncate("hello world", 3, "...")).toBe("...");
  });
});
