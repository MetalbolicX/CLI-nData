#!/usr/bin/env deno

import { parseArgs } from "@std/cli";
import {
  renderBarChart,
  renderBulletChart,
  renderPieChart,
  renderGaugeChart,
  renderScatterPlot
} from "chartex";
import {
  type BarChartDatum,
  type BulletChartDatum,
  type PieChartDatum,
  type GaugeChartDatum,
  type ScatterPlotDatum,
  type BarChartOptions,
  type GaugeChartOptions,
} from "chartex";

interface InputData {
  x?: number | string;
  y?: number;
  [key: string]: unknown;
}

/**
 * Validates and parses JSON input data.
 * @param data - Raw JSON string to validate
 * @returns Parsed data array
 */
const validateJson = (data: string): InputData[] => {
  try {
    const parsed = JSON.parse(data);
    if (!Array.isArray(parsed)) {
      throw new Error("Data must be an array");
    }
    return parsed;
  } catch (error) {
    console.error(`Error: Invalid JSON data - ${error.message}`);
    Deno.exit(1);
  }
};

/**
 * Transforms input data to bar chart format.
 * @param data - Input data array
 * @param xkey - Key for labels
 * @param ykey - Key for values
 * @returns Bar chart data array
 */
const transformToBarChart = (data: InputData[], xkey: string, ykey: string): BarChartDatum[] =>
  data.map(item => ({
    key: String(item[xkey] || ""),
    value: Number(item[ykey] || 0),
    style: "█"
    // style: "*"
  }));

/**
 * Transforms input data to bullet chart format.
 * @param data - Input data array
 * @param xkey - Key for labels
 * @param ykey - Key for values
 * @returns Bullet chart data array
 */
const transformToBulletChart = (data: InputData[], xkey: string, ykey: string): BulletChartDatum[] =>
  data.map(item => ({
    key: String(item[xkey] || ""),
    value: Number(item[ykey] || 0),
    style: "█"
  }));

/**
 * Transforms input data to pie chart format.
 * @param data - Input data array
 * @param xkey - Key for labels
 * @param ykey - Key for values
 * @returns Pie chart data array
 */
const transformToPieChart = (data: InputData[], xkey: string, ykey: string): PieChartDatum[] =>
  data.map((item, index) => ({
    key: String(item[xkey] || ""),
    value: Number(item[ykey] || 0),
    style: ["█", "▓", "▒", "░", "▄", "▌", "▐", "▀"][index % 8]
  }));

/**
 * Transforms input data to gauge chart format.
 * @param data - Input data array
 * @param ykey - Key for values
 * @returns Gauge chart data array
 */
const transformToGaugeChart = (data: InputData[], ykey: string): GaugeChartDatum[] =>
  data.map(item => ({
    key: "gauge",
    value: Number(item[ykey] || 0) / 100, // Normalize to 0-1 range
    style: "█"
  }));

/**
 * Transforms input data to scatter plot format.
 * @param data - Input data array
 * @param xkey - Key for x coordinates
 * @param ykey - Key for y coordinates
 * @returns Scatter plot data array
 */
const transformToScatterPlot = (data: InputData[], xkey: string, ykey: string): ScatterPlotDatum[] =>
  data.map(item => ({
    key: "data",
    value: [Number(item[xkey] || 0), Number(item[ykey] || 0)] as [number, number],
    // style: "+",
    // sides: [1, 1] as [number, number]
  }));

/**
 * Renders a bar chart.
 * @param data - Chart data
 * @param title - Chart title
 */
const plotBarChart = (data: BarChartDatum[], title: string): void => {
  if (title) console.log(`\n${title}\n`);

  const options: BarChartOptions = {
    barWidth: 3,
    height: 15,
    padding: 3
  };

  console.log(renderBarChart(data, options));
};

/**
 * Renders a bullet chart.
 * @param data - Chart data
 * @param title - Chart title
 */
const plotBulletChart = (data: BulletChartDatum[], title: string): void => {
  if (title) console.log(`\n${title}\n`);

  // const options: BulletChartOptions = {
  //   barWidth: 20,
  //   width: 50,
  //   padding: 1
  // };

  console.log(renderBulletChart(data));
};

/**
 * Renders a pie chart.
 * @param data - Chart data
 * @param title - Chart title
 */
const plotPieChart = (data: PieChartDatum[], title: string): void => {
  if (title) console.log(`\n${title}\n`);

  // const options: PieChartOptions = {
  //   radius: 10,
  //   left: 5
  // };

  console.log(renderPieChart(data));
};

/**
 * Renders a gauge chart.
 * @param data - Chart data
 * @param title - Chart title
 */
const plotGaugeChart = (data: GaugeChartDatum[], title: string): void => {
  if (title) console.log(`\n${title}\n`);

  const options: GaugeChartOptions = {
    radius: 10,
    left: 5,
    style: "█"
  };

  console.log(renderGaugeChart(data, options));
};

/**
 * Renders a scatter plot.
 * @param data - Chart data
 * @param title - Chart title
 */
const plotScatterPlot = (data: ScatterPlotDatum[], title: string): void => {
  if (title) console.log(`\n${title}\n`);

  // const options: ScatterPlotOptions = {
  //   width: 60,
  //   height: 20,
  //   style: "+",
  //   hAxis: ["", "", ""],
  //   vAxis: ["", ""],
  //   ratio: [1, 1] as [number, number]
  // };

  console.log(renderScatterPlot(data));
};

/**
 * Main function that handles command line arguments and plotting.
 */
const main = async (): Promise<void> => {
  const args = parseArgs(Deno.args, {
    string: ["type", "data", "title", "xkey", "ykey"],
    boolean: ["help"],
    alias: {
      help: "h",
      type: "t",
      data: "d",
      title: "T",
      xkey: "x",
      ykey: "y"
    },
  });

  if (args.help) {
    console.log(`
Usage: plot [options]

Options:
  -h, --help              Show this help message
  -t, --type <type>       Type of plot (bar, bullet, pie, gauge, scatter)
  -d, --data <file>       Input data file (JSON format, defaults to stdin)
  -T, --title <title>     Title of the chart
  -x, --xkey <key>        Key for X-axis values in JSON data (default: "x")
  -y, --ykey <key>        Key for Y-axis values in JSON data (default: "y")

Supported plot types:
  - bar: Vertical bar chart
  - bullet: Horizontal bullet chart
  - pie: Pie chart
  - gauge: Gauge chart (values 0-100)
  - scatter: Scatter plot

Example:
  echo '[{"x": "A", "y": 30}, {"x": "B", "y": 20}]' | deno run plot -t bar -T "Sample Chart"
    `);
    Deno.exit(0);
  }

  const plotType = args.type || "bar";
  const title = args.title || "";
  const xkey = args.xkey || "x";
  const ykey = args.ykey || "y";

  // Read data from file or stdin
  let rawData: string;
  if (args.data) {
    try {
      rawData = await Deno.readTextFile(args.data);
    } catch (error) {
      console.error(`Error reading file: ${error.message}`);
      Deno.exit(1);
    }
  } else {
    const decoder = new TextDecoder();
    const buffer = new Uint8Array(1024 * 1024); // 1MB buffer
    let totalBytes = 0;
    const chunks: Uint8Array[] = [];

    while (true) {
      const bytesRead = await Deno.stdin.read(buffer);
      if (bytesRead === null) break;

      chunks.push(buffer.slice(0, bytesRead));
      totalBytes += bytesRead;
    }

    const combined = new Uint8Array(totalBytes);
    let offset = 0;
    chunks.forEach(chunk => {
      combined.set(chunk, offset);
      offset += chunk.length;
    });

    rawData = decoder.decode(combined);
  }

  if (!rawData.trim()) {
    console.error("Error: No data provided");
    Deno.exit(1);
  }

  const data = validateJson(rawData);

  if (data.length === 0) {
    console.error("Error: Empty data array");
    Deno.exit(1);
  }

  // Plot strategy mapping
  const plotStrategies = {
    bar: () => plotBarChart(transformToBarChart(data, xkey, ykey), title),
    bullet: () => plotBulletChart(transformToBulletChart(data, xkey, ykey), title),
    pie: () => plotPieChart(transformToPieChart(data, xkey, ykey), title),
    gauge: () => plotGaugeChart(transformToGaugeChart(data, ykey), title),
    scatter: () => plotScatterPlot(transformToScatterPlot(data, xkey, ykey), title)
  };

  const plotFunction = plotStrategies[plotType as keyof typeof plotStrategies];

  if (!plotFunction) {
    console.error(`Error: Plot type '${plotType}' is not supported.`);
    console.error("Supported types: bar, bullet, pie, gauge, scatter");
    Deno.exit(1);
  }

  try {
    plotFunction();
  } catch (error) {
    console.error(`Error rendering chart: ${error.message}`);
    Deno.exit(1);
  }
};

if (import.meta.main) {
  await main();
}