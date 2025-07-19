#!/usr/bin/env deno
"use strict";

/*
* #!/usr/bin/env bash
* # Updated csv2html script
* # readonly UTILS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/utils"
* # exec "$UTILS_DIR/python-runner" "csv2html" "$@"
*/

import { CsvParseStream } from "@std/csv/parse-stream";

/**
 * Reads CSV data from stdin and outputs a semantic HTML table.
 */
const readStdin = async () => {
  const decoder = new TextDecoder();
  let csvText = "";
  for await (const chunk of Deno.stdin.readable) {
    csvText += decoder.decode(chunk);
  }
  return csvText;
};

/**
 * Converts CSV rows to a semantic HTML table string.
 * @param {Array<Record<string, string>>} rows - Array of CSV row objects
 * @returns {string} HTML table string
 */
const csvRowsToHtmlTable = (rows) => {
  if (!rows.length) return "<table></table>";
  const columns = Object.keys(rows[0]);
  const thead = `<thead><tr>${columns
    .map((col) => `<th scope=\"col\">${col}</th>`)
    .join("")}</tr></thead>`;
  const tbody = `<tbody>${rows
    .map(
      (row) =>
        `<tr>${columns.map((col) => `<td>${row[col]}</td>`).join("")}</tr>`
    )
    .join("")}</tbody>`;
  return `<table>${thead}${tbody}</table>`;
};

const main = async () => {
  const csvText = await readStdin();
  const source = ReadableStream.from([csvText]);
  const stream = source.pipeThrough(new CsvParseStream({}));
  const rows = await Array.fromAsync(stream);
  const htmlTable = csvRowsToHtmlTable(rows);
  console.log(htmlTable);
};

main();
