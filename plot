#!/usr/bin/env deno

import { parseArgs } from "@std/cli";
import { readAll } from "@std/io";
import { bar, transformChartData, sparkline, bullet, scatter } from "chartex";

const VALID_CHART_TYPES = ["vertical_bar", "line", "scatter", "horizontal_bar"];

/**
 * Retrieves and parses the data input for the chart.
 * @param args {Record<string, any>} The command-line arguments.
 * @returns {Promise<aObject[]>} The parsed data input.
 */
const getDataInput = async (args) => {
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

/**
 * Displays the help message for the chart command.
 * @returns {void}
 */
const showHelp = () =>
  console.log(`
Usage: chart [options]
Options:
  -h, --help          Show this help message
  -t, --type          Specify the type of chart (e.g., vertical_bar, line, pie)
  -d, --data          Provide data for the chart in JSON format
  -T, --Title         Set the title of the chart
  -x, --xkey          Specify the key for the x-axis
  -y, --ykey          Specify the key for the y-axis
  `);

const options = {
  boolean: ["help"],
  string: ["type", "data", "Title", "xkey", "ykey"],
  alias: {
    h: "help",
    t: "type",
    d: "data",
    T: "Title",
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
const renderVerticalBarChart = (data, xkey, ykey) => {
  if (!(xkey.length && ykey.length)) {
    console.error(
      "Error: --xkey and --ykey are required for vertical bar charts."
    );
    Deno.exit(1);
  }
  console.log(bar(transformChartData(data, xkey, ykey)));
};

/**
 * Renders a line chart.
 * @param data {Object[]} - The data to be visualized.
 * @param xkey {string} - The key for the x-axis.
 * @param ykey {string} - The key for the y-axis.
 * @returns {void} A void function that renders the chart.
 */
const renderLineChart = (data, xkey, ykey) => {
  if (!(xkey.length && ykey.length)) {
    console.error("Error: --xkey and --ykey are required for line charts.");
    Deno.exit(1);
  }
  console.log(sparkline(transformChartData(data, xkey, ykey)));
};

/** * Renders a horizontal bar chart.
 * @param data {Object[]} - The data to be visualized.
 * @param xkey {string} - The key for the x-axis.
 * @param ykey {string} - The key for the y-axis.
 * @returns {void} A void function that renders the chart.
 */
const renderHorizontalBarChart = (data, xkey, ykey) => {
  if (!(xkey.length && ykey.length)) {
    console.error(
      "Error: --xkey and --ykey are required for horizontal bar charts."
    );
    Deno.exit(1);
  }
  console.log(bullet(transformChartData(data, xkey, ykey)));
};

/** * Renders a scatter chart.
 * @param data {Object[]} - The data to be visualized.
 * @param xkey {string} - The key for the x-axis.
 * @param ykey {string} - The key for the y-axis.
 * @returns {void} A void function that renders the chart.
 */
const renderScatterChart = (data, xkey, ykey) => {
  if (!(xkey.length && ykey.length)) {
    console.error("Error: --xkey and --ykey are required for scatter charts.");
    Deno.exit(1);
  }
  console.log(scatter(transformChartData(data, xkey, ykey)));
};

const chartRenderers = {
  vertical_bar: renderVerticalBarChart(data, xkey, ykey),
  line: renderLineChart(data, xkey, ykey),
  horizontal_bar: renderHorizontalBarChart(data, xkey, ykey),
  scatter: renderScatterChart(data, xkey, ykey),
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

  if (!args.type?.length) {
    console.error("Error: --type is a required option.");
    Deno.exit(1);
  }

  if (!VALID_CHART_TYPES.includes(args.type)) {
    console.error(
      `Error: Invalid chart type. Supported types are: ${VALID_CHART_TYPES.join(
        ", "
      )}`
    );
    Deno.exit(1);
  }

  const dataInput = await getDataInput(args);

  const renderChart = chartRenderers[args.type];
  if (renderChart) {
    renderChart(dataInput, args.xkey, args.ykey);
  } else {
    console.error(`Error: Chart type ${args.type} is not implemented yet.`);
    Deno.exit(1);
  }
};

if (import.meta.main) {
  main();
}
