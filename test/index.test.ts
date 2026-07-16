import { describe, it, expect } from "vitest";
import * as api from "../src/index.js";

describe("public API (index)", () => {
  it("exports slugify and sum", () => {
    expect(typeof api.slugify).toBe("function");
    expect(typeof api.sum).toBe("function");
  });

  it("re-exports wire through to the implementations", () => {
    expect(api.slugify("Hello World")).toBe("hello-world");
    expect(api.sum([1, 2, 3])).toBe(6);
  });
});
