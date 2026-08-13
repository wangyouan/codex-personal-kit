#!/usr/bin/env node
import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const TABLE_TYPES = new Set(["regression", "descriptive", "correlation", "variable_definition", "difference", "robustness"]);

function parseArgs(argv) {
  if (argv.length < 2) throw new Error("Usage: build_xlsx.mjs INPUT.json OUTPUT.xlsx [--mode publication|working-shell] [--preview-dir DIR] [--force]");
  const opts = { input: argv[0], output: argv[1], mode: null, previewDir: null, force: false };
  for (let i = 2; i < argv.length; i += 1) {
    if (argv[i] === "--mode") opts.mode = argv[++i];
    else if (argv[i] === "--preview-dir") opts.previewDir = argv[++i];
    else if (argv[i] === "--force") opts.force = true;
    else throw new Error(`Unknown option: ${argv[i]}`);
  }
  if (opts.mode && !["publication", "working-shell"].includes(opts.mode)) throw new Error("mode must be publication or working-shell");
  return opts;
}

function validate(spec) {
  const errors = [];
  for (const field of ["version", "table_type", "language", "label", "title", "columns", "rows"]) {
    if (!(field in spec)) errors.push(`missing ${field}`);
  }
  if (!TABLE_TYPES.has(spec.table_type)) errors.push(`unsupported table_type ${spec.table_type}`);
  if (!Array.isArray(spec.columns) || spec.columns.length === 0) errors.push("columns must be non-empty");
  if (!Array.isArray(spec.rows)) errors.push("rows must be an array");
  if (["regression", "robustness"].includes(spec.table_type)) {
    if (!spec.inference?.statistic_type || !spec.inference?.cluster || !spec.inference?.significance) errors.push("regression-style tables require complete inference metadata");
  }
  return errors;
}

function colName(index) {
  let n = index + 1;
  let name = "";
  while (n > 0) {
    const rem = (n - 1) % 26;
    name = String.fromCharCode(65 + rem) + name;
    n = Math.floor((n - 1) / 26);
  }
  return name;
}

function contiguousGroups(columns) {
  const groups = [];
  for (const col of columns) {
    const name = String(col.group ?? "");
    if (groups.length && groups.at(-1).name === name) groups.at(-1).count += 1;
    else groups.push({ name, count: 1 });
  }
  return groups;
}

function cellPayload(cell) {
  if (cell == null) return { value: null, format: null, editable: false };
  if (typeof cell !== "object" || Array.isArray(cell)) return { value: cell, format: Number.isInteger(cell) ? "#,##0" : null, editable: false };
  if (cell.display != null) return { value: String(cell.display), format: "@", editable: Boolean(cell.editable) };
  const value = cell.value ?? null;
  const decimals = cell.decimals ?? 3;
  const zeros = decimals > 0 ? `0.${"0".repeat(decimals)}` : "0";
  const stars = String(cell.stars ?? "");
  let format = null;
  if (typeof value === "number") {
    if (cell.parentheses) format = `(${zeros});(-${zeros});(${zeros})`;
    else if (stars) format = `${zeros}"${stars}";-${zeros}"${stars}";${zeros}`;
    else if (Number.isInteger(value) && decimals === 0) format = "#,##0";
    else format = `${zeros};-${zeros};${zeros}`;
  }
  return { value, format, editable: Boolean(cell.editable) };
}

function safeSheetName(spec, used) {
  const base = String(spec.label || spec.title || "Table").replace(/[\\/*?:[\]]/g, "-").slice(0, 31) || "Table";
  let name = base;
  let suffix = 2;
  while (used.has(name)) {
    const tail = `-${suffix++}`;
    name = `${base.slice(0, 31 - tail.length)}${tail}`;
  }
  used.add(name);
  return name;
}

async function addSpecSheet(workbook, spec, usedNames, requestedMode) {
  const errors = validate(spec);
  if (errors.length) throw new Error(`${spec.label || spec.title}: ${errors.join("; ")}`);
  const mode = requestedMode || spec.mode || "publication";
  const sheetName = safeSheetName(spec, usedNames);
  const sheet = workbook.worksheets.add(sheetName);
  sheet.showGridLines = false;
  const totalCols = spec.columns.length + 1;
  const lastCol = colName(totalCols - 1);
  let row = 1;
  const merges = [];
  const headerRows = [];
  const panelRows = [];
  const editableCells = [];

  sheet.getRange(`A${row}:${lastCol}${row}`).merge();
  sheet.getRange(`A${row}`).values = [[`${spec.label}  ${spec.title}`]];
  const titleRow = row++;
  if (spec.caption_note) {
    sheet.getRange(`A${row}:${lastCol}${row}`).merge();
    sheet.getRange(`A${row}`).values = [[String(spec.caption_note)]];
    row += 1;
  }
  if (mode === "working-shell") {
    for (const [label, value] of [["PURPOSE", spec.purpose || "State the table's role in the paper."], ["EXPECTED RESULT", spec.expected_result || "State the expected empirical pattern without inventing values."]]) {
      sheet.getRange(`A${row}:${lastCol}${row}`).merge();
      sheet.getRange(`A${row}`).values = [[`${label}: ${value}`]];
      row += 1;
    }
  }
  const groups = contiguousGroups(spec.columns);
  if (groups.some(group => group.name)) {
    let cursor = 2;
    sheet.getRange(`A${row}`).values = [[""]];
    for (const group of groups) {
      const start = colName(cursor - 1);
      const end = colName(cursor + group.count - 2);
      if (group.count > 1) sheet.getRange(`${start}${row}:${end}${row}`).merge();
      sheet.getRange(`${start}${row}`).values = [[group.name]];
      cursor += group.count;
    }
    headerRows.push(row++);
  }
  if (spec.columns.some(col => col.model)) {
    const values = ["", ...spec.columns.map(col => col.model || "")];
    sheet.getRange(`A${row}:${lastCol}${row}`).values = [values];
    headerRows.push(row++);
  }
  const variable = spec.language === "zh" ? "变量" : "Variables";
  sheet.getRange(`A${row}:${lastCol}${row}`).values = [[variable, ...spec.columns.map(col => col.label || "")]];
  headerRows.push(row++);
  const firstDataRow = row;
  for (const rowSpec of spec.rows) {
    if (rowSpec.kind === "spacer") {
      row += 1;
      continue;
    }
    if (rowSpec.kind === "panel") {
      sheet.getRange(`A${row}:${lastCol}${row}`).merge();
      sheet.getRange(`A${row}`).values = [[String(rowSpec.label || "")]];
      panelRows.push(row++);
      continue;
    }
    const values = [String(rowSpec.label || "")];
    const formats = ["@"];
    for (let i = 0; i < spec.columns.length; i += 1) {
      const key = spec.columns[i].key;
      const payload = cellPayload(rowSpec.values?.[key]);
      values.push(payload.value);
      formats.push(payload.format || (typeof payload.value === "number" ? "0.000" : "@"));
      if (payload.editable || (mode === "working-shell" && payload.value == null)) editableCells.push(`${colName(i + 1)}${row}`);
    }
    sheet.getRange(`A${row}:${lastCol}${row}`).values = [values];
    for (let i = 0; i < formats.length; i += 1) sheet.getRange(`${colName(i)}${row}`).format.numberFormat = formats[i];
    row += 1;
  }
  const lastDataRow = Math.max(firstDataRow, row - 1);
  if (spec.notes?.length) {
    sheet.getRange(`A${row}:${lastCol}${row}`).merge();
    const prefix = spec.language === "zh" ? "注：" : "Notes: ";
    sheet.getRange(`A${row}`).values = [[prefix + spec.notes.join(" ")]];
    sheet.getRange(`A${row}`).format.wrapText = true;
    row += 1;
  }
  const used = sheet.getRange(`A1:${lastCol}${row - 1}`);
  used.format.font = { name: "Times New Roman", size: spec.language === "zh" ? 9 : 10, color: "#000000" };
  used.format.verticalAlignment = "center";
  sheet.getRange(`A1:A${row - 1}`).format.horizontalAlignment = "left";
  if (totalCols > 1) sheet.getRange(`B1:${lastCol}${row - 1}`).format.horizontalAlignment = "center";
  sheet.getRange(`A${titleRow}:${lastCol}${titleRow}`).format.font = { name: "Times New Roman", size: 11, bold: true, color: "#000000" };
  sheet.getRange(`A${titleRow}:${lastCol}${titleRow}`).format.horizontalAlignment = "center";
  for (const headerRow of headerRows) {
    sheet.getRange(`A${headerRow}:${lastCol}${headerRow}`).format.font = { name: "Times New Roman", size: spec.language === "zh" ? 9 : 10, bold: true, color: "#000000" };
  }
  for (const panelRow of panelRows) {
    sheet.getRange(`A${panelRow}:${lastCol}${panelRow}`).format.font = { name: "Times New Roman", size: spec.language === "zh" ? 9 : 10, bold: true, color: "#000000" };
    sheet.getRange(`A${panelRow}:${lastCol}${panelRow}`).format.borders = { top: { style: "thin", color: "#000000" } };
  }
  if (headerRows.length) {
    sheet.getRange(`A${headerRows[0]}:${lastCol}${headerRows[0]}`).format.borders = { top: { style: "medium", color: "#000000" } };
    const lastHeader = headerRows.at(-1);
    sheet.getRange(`A${lastHeader}:${lastCol}${lastHeader}`).format.borders = { bottom: { style: "thin", color: "#000000" } };
  }
  sheet.getRange(`A${lastDataRow}:${lastCol}${lastDataRow}`).format.borders = { bottom: { style: "medium", color: "#000000" } };
  sheet.getRange(`A1:A${row - 1}`).format.columnWidth = spec.table_type === "variable_definition" ? 28 : 24;
  if (totalCols > 1) sheet.getRange(`B1:${lastCol}${row - 1}`).format.columnWidth = spec.table_type === "variable_definition" ? 34 : 15;
  used.format.autofitRows();
  for (const address of editableCells) sheet.getRange(address).format.fill = "#FFF2CC";
  return { sheetName, range: `A1:${lastCol}${row - 1}` };
}

async function main() {
  const opts = parseArgs(process.argv.slice(2));
  try {
    await fs.access(opts.output);
    if (!opts.force) throw new Error(`output exists: ${opts.output}; use --force to replace`);
  } catch (error) {
    if (error.code !== "ENOENT" && !String(error.message).includes("use --force")) throw error;
    if (String(error.message).includes("use --force")) throw error;
  }
  const inputStat = await fs.stat(opts.input);
  const inputFiles = inputStat.isDirectory()
    ? (await fs.readdir(opts.input)).filter(name => name.endsWith(".json")).sort().map(name => path.join(opts.input, name))
    : [opts.input];
  const specs = [];
  for (const inputFile of inputFiles) {
    const parsed = JSON.parse(await fs.readFile(inputFile, "utf8"));
    specs.push(...(Array.isArray(parsed) ? parsed : [parsed]));
  }
  if (!specs.length) throw new Error("no JSON table specifications found");
  const workbook = Workbook.create();
  const usedNames = new Set();
  const built = [];
  for (const spec of specs) built.push(await addSpecSheet(workbook, spec, usedNames, opts.mode));
  for (const item of built) {
    const inspection = await workbook.inspect({ kind: "table", range: `${item.sheetName}!${item.range}`, include: "values,formulas", tableMaxRows: 30, tableMaxCols: 12 });
    process.stdout.write(`${inspection.ndjson}\n`);
  }
  const errorScan = await workbook.inspect({ kind: "match", searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A", options: { useRegex: true, maxResults: 100 }, summary: "formula error scan" });
  process.stdout.write(`${errorScan.ndjson}\n`);
  if (opts.previewDir) {
    await fs.mkdir(opts.previewDir, { recursive: true });
    for (const item of built) {
      const blob = await workbook.render({ sheetName: item.sheetName, range: item.range, scale: 2, format: "png" });
      await fs.writeFile(path.join(opts.previewDir, `${item.sheetName}.png`), new Uint8Array(await blob.arrayBuffer()));
    }
  }
  await fs.mkdir(path.dirname(path.resolve(opts.output)), { recursive: true });
  const file = await SpreadsheetFile.exportXlsx(workbook);
  await file.save(opts.output);
  process.stdout.write(`OK: wrote ${opts.output}\n`);
}

main().catch(error => {
  process.stderr.write(`ERROR: ${error.stack || error.message}\n`);
  process.exitCode = 1;
});
