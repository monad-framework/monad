export function parseTsv<T extends Record<string, string>>(input: string): T[] {
  const lines = input.split(/\r?\n/).filter((line) => line.trim().length > 0);

  const header = lines.shift();

  if (!header) {
    return [];
  }

  const columns = header.split("\t");

  return lines.map((line) => {
    const values = line.split("\t");

    return Object.fromEntries(
      columns.map((column, index) => [column, values[index] ?? ""]),
    ) as T;
  });
}
