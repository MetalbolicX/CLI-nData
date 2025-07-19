#!/usr/bin/env -S deno run -W
"use strict";

/*
* #!/usr/bin/env bash
* # Updated csv2html script
* # readonly UTILS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/utils"
* # exec "$UTILS_DIR/python-runner" "csv2html" "$@"
*/

import { CsvParseStream } from "@std/csv/parse-stream";
import { parseArgs } from "@std/cli";

/**
 * Displays the help message for the chart command.
 * @returns {void}
 */
const showHelp = () =>
  console.log(`
Usage: csv2html [options]
Options:
    -h, --help          Show this help message
    -o, --output        Specify the output file (default: stdout).
    -d, --delimiter     Specify the CSV delimiter (default: ',').
    -H, --header        Specify if the files does not have a header row.
    -f, --fields        Specify the fields to include as a number (default: 0, it mean all).
  `);

const options = {
  boolean: ["help", "header"],
  string: ["output", "delimiter", "fields"],
  alias: {
    h: "help",
    o: "output",
    d: "delimiter",
    H: "header",
    f: "fields",
  },
};


/**
 * Reads CSV data from stdin and outputs a semantic HTML table.
 */
const readStdin = async () => {
  const decoder = new TextDecoder();
  const chunks = await Array.fromAsync(Deno.stdin.readable);
  return chunks.map(chunk => decoder.decode(chunk)).join("");
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
    .map((col) => `<th>${col}</th>`)
    .join("")}</tr></thead>`;
  const tbody = `<tbody>${rows
    .map(
      (row) =>
        `<tr>${columns.map((col) => `<td>${row[col]}</td>`).join("")}</tr>`
    )
    .join("")}</tbody>`;
  // return `<table>${thead}${tbody}</table>`;
  return /*html*/`
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <link rel="stylesheet" href="https://unpkg.com/@colinaut/action-table/dist/action-table.css">
  <script type="module" src="https://unpkg.com/@colinaut/action-table/dist/index.js"></script>
  <title>CSV to HTML Table</title>
</head>
<body>
  <action-table>
    <table>
      ${thead}${tbody}
    </table>
  </action-table>
</body>
</html>`;
};

/** * Main function to parse command line arguments and convert CSV to HTML.
 * @returns {Promise<void>} Resolves when the operation is complete.
 */
const main = async () => {
  const args = parseArgs(Deno.args, options);

  if (args.help) {
    showHelp();
    Deno.exit(0);
  }

  const csvText = await readStdin();
  const source = ReadableStream.from([csvText]);

  const stream = source.pipeThrough(new CsvParseStream({
    separator: args.delimiter || ",",
    trimLeadingSpace: true,
    fieldsPerRecord: parseInt(args.fields, 10) || 0, // Auto-detect number of fields
    skipFirstRow: !args.header,
  }));

  const rows = await Array.fromAsync(stream);
  const htmlTable = csvRowsToHtmlTable(rows);

  if (args.output?.length) {
    await Deno.writeTextFile(args.output, htmlTable);
    return;
  }
  console.log(htmlTable);
};

if (import.meta.main) {
  main()
}