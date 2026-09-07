import { describe, expect, test } from "bun:test";

import { parseTsv } from "./tsv";

describe("parseTsv", () => {
  test("parses rows using the header as keys", () => {
    const rows = parseTsv<Record<string, string>>(
      "id\tstatus\ttitle\nWP-001\tREADY\tFirst packet\nWP-002\tCLOSED\tSecond packet\n",
    );

    expect(rows).toEqual([
      {
        id: "WP-001",
        status: "READY",
        title: "First packet",
      },
      {
        id: "WP-002",
        status: "CLOSED",
        title: "Second packet",
      },
    ]);
  });

  test("returns an empty array for empty input", () => {
    expect(parseTsv<Record<string, string>>("\n\n")).toEqual([]);
  });

  test("preserves empty cells instead of shifting columns", () => {
    const rows = parseTsv<Record<string, string>>(
      "id\tpath\tstatus\nEVID-001\t\tPASSED\n",
    );

    expect(rows[0]).toEqual({
      id: "EVID-001",
      path: "",
      status: "PASSED",
    });
  });
});
