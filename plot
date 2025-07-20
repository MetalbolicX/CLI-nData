#!/usr/bin/env deno

import { parseArgs } from "@std/cli";
import { readAll } from "@std/io";
import { bar, transformChartData, sparkline, bullet, scatter } from "chartex";

const VALID_CHART_TYPES = ["vertical_bar", "line", "scatter", "horizontal_bar"];

/** * A utility function to create a pipeline of functions.
 * It takes multiple functions as arguments and returns
 * a new function that applies them sequentially to an input value.
 * @param {...Function} fns - The functions to be pipelined.
 * @returns {Function} A function that takes an input and applies the pipelined functions.
 */
const pipe = (...fns) => (x) =>
  fns.reduce((v, f) => f(v), x);

/**
 * Retrieves and parses the data input for the chart.
 * @param args {Record<string, any>} The command-line arguments.
 * @returns {Promise<aObject[]>} The parsed data input.
 */
const getDataInput = async (args) => {
  // const getDataInput = async () => {
  if (typeof args.data === "string" && args.data.trim().length > 0) {
    try {
      return JSON.parse(args.data);
    } catch (error) {
      console.error(
        `Error: Invalid JSON data provided in --data. ${error.message}`
      );
      Deno.exit(1);
    }
  }

  const buffer = await readAll(Deno.stdin);
  const input = new TextDecoder().decode(buffer).trim();

  if (!input) {
    console.error("Error: No data provided via --data or stdin.");
    Deno.exit(1);
  }

  try {
    return JSON.parse(input);
  } catch (error) {
    console.error(
      `Error: Invalid JSON data provided via stdin. ${error.message}`
    );
    Deno.exit(1);
  }
};

/** * Validates the chart arguments to ensure they are correct.
 * @param args {Record<string, any>} The command-line arguments.
 * @returns {void} A void function that exits the process if validation fails.
 */
const validateChartArguments = (args) => {
  if (!(args.type?.length && VALID_CHART_TYPES.includes(args.type))) {
    console.error(
      `Error: Invalid or missing chart type. Supported types are: ${VALID_CHART_TYPES.join(
        ", "
      )}`
    );
    Deno.exit(1);
  }

  if (!args.xkey || !args.ykey) {
    console.error("Error: --xkey and --ykey are required options.");
    Deno.exit(1);
  }
};


/**
 * Displays the help message for the chart command.
 * @returns {void}
 */
const showHelp = () =>
  console.log(`
Usage: chart [options]
Options:
  -d, --data          Provide data for the chart in JSON format
  -h, --help          Show this help message
  -T, --Title         Set the title of the chart
  -t, --type          Specify the type of chart (e.g., vertical_bar, line, pie)
  -x, --xkey          Specify the key for the x-axis
  -y, --ykey          Specify the key for the y-axis
  `);

const options = {
  boolean: ["help"],
  string: ["type", "data", "Title", "xkey", "ykey"],
  alias: {
    d: "data",
    h: "help",
    T: "Title",
    t: "type",
    x: "xkey",
    y: "ykey",
  },
};

/**
 * Renders a vertical bar chart.
 * @param data {Object[]} - The data to be visualized.
 * @param xkey {string} - The key for the x-axis.
 * @param ykey {string} - The key for the y-axis.
 * @returns {void} A void function that renders the chart.
 */
const renderVerticalBarChart = (data, xkey, ykey) =>
  pipe(
    (d) => transformChartData(d, xkey, ykey),
    bar,
    console.log
  )(data);

/**
 * Renders a line chart.
 * @param data {Object[]} - The data to be visualized.
 * @param xkey {string} - The key for the x-axis.
 * @param ykey {string} - The key for the y-axis.
 * @returns {void} A void function that renders the chart.
 */
const renderLineChart = (data, xkey, ykey) =>
  pipe(
    (d) => transformChartData(d, xkey, ykey),
    (chartData) => sparkline(chartData, { width: 40, height: 15 }),
    console.log
  )(data);

/** * Renders a horizontal bar chart.
 * @param data {Object[]} - The data to be visualized.
 * @param xkey {string} - The key for the x-axis.
 * @param ykey {string} - The key for the y-axis.
 * @returns {void} A void function that renders the chart.
 */
const renderHorizontalBarChart = (data, xkey, ykey) =>
  pipe(
    (d) => transformChartData(d, xkey, ykey),
    bullet,
    console.log
  )(data);

/** * Renders a scatter chart.
 * @param data {Object[]} - The data to be visualized.
 * @param xkey {string} - The key for the x-axis.
 * @param ykey {string} - The key for the y-axis.
 * @returns {void} A void function that renders the chart.
 */
const renderScatterChart = (data, xkey, ykey) =>
  pipe(
    (d) => transformChartData(d, xkey, ykey),
    scatter,
    console.log
  )(data);

const chartRenderers = {
  vertical_bar: renderVerticalBarChart,
  line: renderLineChart,
  horizontal_bar: renderHorizontalBarChart,
  scatter: renderScatterChart,
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

  const dataInput = getDataInput(args);

  validateChartArguments(args);

  const renderChart = chartRenderers[args.type];
  if (renderChart) {
    renderChart(await dataInput, args.xkey, args.ykey);
  } else {
    console.error(`Error: Chart type ${args.type} is not implemented yet.`);
    Deno.exit(1);
  }
};

if (import.meta.main) {
  main();
}
