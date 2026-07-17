import { describe, it, expect } from "vitest";
import { sum, mean, median } from "../src/math.js";

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

  it("returns the element itself for a single-item list", () => {
    expect(sum([42])).toBe(42);
  });
});

describe("mean", () => {
  it("returns 0 for an empty list", () => {
    expect(mean([])).toBe(0);
  });

  it("returns the element itself for a single-item list", () => {
    expect(mean([42])).toBe(42);
  });

  it("computes the mean of an odd-length list", () => {
    expect(mean([1, 2, 3])).toBe(2);
  });

  it("computes the mean of an even-length list", () => {
    expect(mean([1, 2, 3, 4])).toBe(2.5);
  });
});

describe("median", () => {
  it("returns 0 for an empty list", () => {
    expect(median([])).toBe(0);
  });

  it("returns the element itself for a single-item list", () => {
    expect(median([42])).toBe(42);
  });

  it("returns the middle value of an odd-length list", () => {
    expect(median([5, 1, 3])).toBe(3);
  });

  it("averages the two middle values of an even-length list", () => {
    expect(median([1, 2, 3, 4])).toBe(2.5);
  });

  it("does not mutate the input array while sorting", () => {
    const input = [3, 1, 2];
    median(input);
    expect(input).toEqual([3, 1, 2]);
  });
});
