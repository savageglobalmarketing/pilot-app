import { describe, it, expect } from "vitest";
import { clamp } from "../src/clamp.js";

describe("clamp", () => {
  it("returns min when value is below range", () => {
    expect(clamp(-5, 0, 10)).toBe(0);
  });

  it("returns value unchanged when within range", () => {
    expect(clamp(5, 0, 10)).toBe(5);
  });

  it("returns max when value is above range", () => {
    expect(clamp(15, 0, 10)).toBe(10);
  });

  it("returns min at the lower boundary", () => {
    expect(clamp(0, 0, 10)).toBe(0);
  });

  it("returns max at the upper boundary", () => {
    expect(clamp(10, 0, 10)).toBe(10);
  });

  it("throws a clear Error when min > max", () => {
    expect(() => clamp(5, 10, 0)).toThrow(
      "clamp: min (10) must not be greater than max (0)",
    );
  });
});
