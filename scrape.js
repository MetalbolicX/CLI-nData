#!/usr/bin/env -S deno run --allow-env

import { parseArgs } from "@std/cli";
import { readAll } from "@std/io";
import { parse } from "node-html-parser";
import xPathToCss from "xpath-to-css";

const VALID_OUTPUTS = ["stdout", "html", "json", "csv", "text"];
const XPATH_PREFIX = "//";
/** Parses the HTML input from either a file or stdin.
 * @param {Object} args - The command line arguments.
 * @returns {Promise<HTMLElement>} The parsed HTML root element.
 */
const parseHTML = async (args) => {
  if (typeof args.html === "string" && args.html.trim().length > 0) {
    const root = parse(args.html);
    return root;
  }

  const buffer = await readAll(Deno.stdin);
  const input = new TextDecoder().decode(buffer).trim();

  if (!input) {
    console.error("Error: No data provided via --data or stdin.");
    Deno.exit(1);
  }

  const root = parse(input);
  return root;
};

/**
 * Displays the help message for the chart command.
 * @returns {void}
 */
const showHelp = () =>
  console.log(`
Usage: scrape [options]
Options:
    -h, --help          Show this help message
    -a, --attribute     Specify the attribute to scrape.
    -e, --selector      Specify the selector to use for scraping.
    -f, --file          Specify the file to scrape.
    -x, --existance     Specify the existance check.
    -r, --raw_input     Specify the raw input to scrape.
    -o, --output        Specify the output file (default: stdout).
    -t, --text          Specify to extract text content.
  `);

const options = {
  boolean: ["help", "existance", "text"],
  string: ["attribute", "selector", "file", "raw_input", "output"],
  alias: {
    h: "help",
    a: "attribute",
    e: "selector",
    f: "file",
    x: "existance",
    r: "raw_input",
    o: "output",
    t: "text",
  },
};

// Case handlers as arrow functions
const handleAttribute = (elements, attribute, selector) => {
  const results = elements
    .map((el) => el.getAttribute(attribute))
    .filter(Boolean);
  if (!results.length) {
    console.error(
      `No attribute '${attribute}' found for selector: ${selector}`
    );
  }
  console.log(results.join("\n"));
};

const handleExistence = (elements, selector) => {
  if (elements.length > 0) {
    Deno.exit(0);
  } else {
    console.error("No elements found for selector: " + selector);
    Deno.exit(1);
  }
};

const handleText = (elements, selector) => {
  const results = elements.map((el) => el.textContent.trim());
  if (!results.length) {
    console.error(`No text content found for selector: ${selector}`);
  }
  console.log(results.join("\n"));
};

const handleDefault = (elements, selector) => {
  if (!elements.length) {
    console.error(`No elements found for selector: ${selector}`);
  }
  console.log(elements.toString());
};

/**
 * Main function to parse arguments and render the chart.
 * @returns {void}
 */
const main = async () => {
  const args = parseArgs(Deno.args, options);

  if (args.help) {
    showHelp();
    Deno.exit(0);
  }

  if (!args.selector?.length) {
    console.error("Error: --selector is a required option.");
    Deno.exit(1);
  }

  const root = await parseHTML(args);
  const selector = args.selector.startsWith(XPATH_PREFIX)
    ? xPathToCss(args.selector)
    : args.selector;

  const elements = root.removeWhitespace().querySelectorAll(selector);

  // Dispatch
  if (args.attribute) {
    handleAttribute(elements, args.attribute, selector);
  } else if (args.existance) {
    handleExistence(elements, selector);
  } else if (args.text) {
    handleText(elements, selector);
  } else {
    handleDefault(elements, selector);
  }
};

if (import.meta.main) {
  main();
}
