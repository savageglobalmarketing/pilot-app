import { describe, it, expect } from "vitest";
import { sum } from "../src/math.js";

describe("sum", () => {
  it("adds a list of positive numbers", () => {
    expect(sum([1, 2, 3, 4])).toBe(10);
  });

  it("handles negative numbers", () => {
    expect(sum([10, -3, -2])).toBe(5);
  });

  it("returns 0 for an empty list", () => {
    expect(sum([])).toBe(0);
  });
});
