#!/usr/bin/env -S deno run --allow-env --allow-write

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
  // If --file is provided, read from file
  if (typeof args.file === "string" && args.file.trim().length > 0) {
    try {
      const fileContent = await Deno.readTextFile(args.file);
      if (!fileContent.trim()) {
        console.error(`Error: File '${args.file}' is empty.`);
        Deno.exit(1);
      }
      return parse(fileContent);
    } catch (err) {
      console.error(
        `Error: Unable to read file '${args.file}'. ${err.message || err}`
      );
      Deno.exit(1);
    }
  }

  // Otherwise, read from stdin
  const buffer = await readAll(Deno.stdin);
  const input = new TextDecoder().decode(buffer).trim();

  if (!input) {
    console.error("Error: No data provided via --file, --html, or stdin.");
    Deno.exit(1);
  }

  return parse(input);
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
    -o, --output        Specify the output file (default: stdout).
    -t, --text          Specify to extract text content.
  `);

const options = {
  boolean: ["help", "existance", "text"],
  string: ["attribute", "selector", "file", "output"],
  alias: {
    h: "help",
    a: "attribute",
    e: "selector",
    f: "file",
    x: "existance",
    o: "output",
    t: "text",
  },
};

/** * Outputs the result to a file or stdout.
 * @param {string} result - The result to output.
 * @param {Object} args - The command line arguments.
 * @returns {Promise<void>}
 */
const outputResult = async (result, args) => {
  if (args.output) {
    try {
      await Deno.writeTextFile(args.output, result);
    } catch (err) {
      console.error(
        `Error: Unable to write to file '${args.output}'. ${err.message || err}`
      );
      Deno.exit(1);
    }
  } else {
    console.log(result);
  }
};

/** * Handles the attribute scraping logic.
 * @param {HTMLElement[]} elements - The elements to scrape.
 * @param {string} attribute - The attribute to scrape.
 * @param {string} selector - The selector used for scraping.
 * @param {Object} args - The command line arguments.
 * @returns {Promise<void>}
 */
const handleAttribute = async (elements, attribute, selector, args) => {
  const results = elements
    .map((el) => el.getAttribute(attribute))
    .filter(Boolean);
  if (!results.length) {
    console.error(
      `No attribute '${attribute}' found for selector: ${selector}`
    );
  }
  await outputResult(results.join("\n"), args);
};

/** * Handles the existence check logic.
 * @param {HTMLElement[]} elements - The elements to check.
 * @param {string} selector - The selector used for checking.
 * @param {Object} args - The command line arguments.
 * @returns {Promise<void>}
 */
const handleExistence = async (elements, selector, args) => {
  if (elements.length > 0) {
    Deno.exit(0);
  } else {
    console.error("No elements found for selector: " + selector);
    Deno.exit(1);
  }
};

/** * Handles the text extraction logic.
 * @param {HTMLElement[]} elements - The elements to extract text from.
 * @param {string} selector - The selector used for scraping.
 * @param {Object} args - The command line arguments.
 * @returns {Promise<void>}
 */
const handleText = async (elements, selector, args) => {
  const results = elements.map((el) => el.textContent.trim());
  if (!results.length) {
    console.error(`No text content found for selector: ${selector}`);
  }
  await outputResult(results.join("\n"), args);
};

/** * Handles the default case when no specific action is specified.
 * @param {HTMLElement[]} elements - The elements to handle.
 * @param {string} selector - The selector used for scraping.
 * @param {Object} args - The command line arguments.
 * @returns {Promise<void>}
 */
const handleDefault = async (elements, selector, args) => {
  if (!elements.length) {
    console.error(`No elements found for selector: ${selector}`);
  }
  await outputResult(elements.toString(), args);
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
    await handleAttribute(elements, args.attribute, selector, args);
  } else if (args.existance) {
    await handleExistence(elements, selector, args);
  } else if (args.text) {
    await handleText(elements, selector, args);
  } else {
    await handleDefault(elements, selector, args);
  }
};

if (import.meta.main) {
  main();
}
