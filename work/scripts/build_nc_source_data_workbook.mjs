#!/usr/bin/env node
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const outputDir = path.join(repoRoot, "outputs/source_data");
const previewDir = path.join(repoRoot, "work/source_data_previews");
const workbookPath = path.join(outputDir, "nc_source_data_v1.xlsx");
const manifestPath = path.join(outputDir, "nc_source_data_manifest.md");

const sources = [
  {
    sheet: "Fig1_TaskMatrix",
    figure: "Figure 1",
    source: "outputs/figure1_dataset_task_matrix.csv",
    notes: "Dataset-task matrix, record counts, target availability and P-window definition summary.",
    status: "included",
  },
  {
    sheet: "Fig2_EarlyWindow",
    figure: "Figure 2",
    source: "outputs/figure2_early_window_performance.csv",
    notes: "Lead-time-dependent early-window performance metrics.",
    status: "included",
  },
  {
    sheet: "Fig3_Heldout",
    figure: "Figure 3",
    source: "outputs/figure3_heldout_generalization.csv",
    notes: "Held-event and held-station generalization metrics.",
    status: "included",
  },
  {
    sheet: "Fig3_BootstrapCI",
    figure: "Figure 3 / Supplement",
    source: "work/ground_motion_balanced_station_10s/held_station_bootstrap_ci.csv",
    notes: "Paired bootstrap confidence intervals for held-station MAE reductions.",
    status: "included",
  },
  {
    sheet: "Fig3_TailAudit",
    figure: "Figure 3 / Supplement",
    source: "work/ground_motion_balanced_station_10s/held_station_tail_audit.csv",
    notes: "Top-tail MAE and factor-of-two underprediction audit.",
    status: "included",
  },
  {
    sheet: "Fig4_ClassicalUnc",
    figure: "Figure 4",
    source: "outputs/figure4_classical_uncertainty.csv",
    notes: "Classical reference and uncertainty calibration figure data.",
    status: "included",
  },
  {
    sheet: "Fig4_CalSize",
    figure: "Figure 4 / Supplement",
    source: "work/nc_calibration_size_audit/target_calibration_size_audit.csv",
    notes: "Target-domain calibration sample-size audit.",
    status: "included",
  },
  {
    sheet: "Fig5_Residuals",
    figure: "Figure 5",
    source: "outputs/figure5_residual_diagnostic_source_data.csv",
    notes: "Residual diagnostic panel source data for error reductions and binned residual curves.",
    status: "included",
  },
  {
    sheet: "Fig6_PhaseAudit",
    figure: "Figure 6",
    source: "outputs/figure6_phase_label_audit.csv",
    notes: "Phase label-domain audit data.",
    status: "included",
  },
  {
    sheet: "Fig7_Boundary",
    figure: "Figure 7",
    source: "outputs/nc_core_predictability_boundary_table.csv",
    notes: "Core predictability-boundary synthesis table.",
    status: "included",
  },
  {
    sheet: "SI_FeatureGroups",
    figure: "Supplement",
    source: "outputs/feature_group_ablation_table.csv",
    notes: "Feature-group ablation across P-only, metadata, distance, site and combined feature families.",
    status: "included",
  },
  {
    sheet: "SI_ESM_Onset",
    figure: "Supplement",
    source: "outputs/esm_p_onset_sensitivity_audit.csv",
    notes: "ESM theoretical P-onset sensitivity audit.",
    status: "included",
  },
  {
    sheet: "SI_ESM_Spotcheck",
    figure: "Supplement",
    source: "outputs/esm_waveform_p_pick_spotcheck.csv",
    notes: "ESM waveform-envelope onset proxy spot audit.",
    status: "included",
  },
  {
    sheet: "SI_EarlyPeak",
    figure: "Supplement",
    source: "outputs/early_window_peak_capture_audit.csv",
    notes: "Early-window peak-capture audit.",
    status: "included",
  },
  {
    sheet: "SI_PhaseTable",
    figure: "Supplement",
    source: "outputs/figures/phase_audit/phase_audit_1000_table.csv",
    notes: "Per-dataset 1,000-record phase-audit table.",
    status: "included",
  },
];

function relPath(absPath) {
  return path.relative(repoRoot, absPath);
}

function isNumberHeader(header) {
  const text = String(header ?? "").toLowerCase();
  return (
    text.includes("coverage") ||
    text.includes("ratio") ||
    text.includes("mae") ||
    text.includes("reduction") ||
    text.includes("score") ||
    text.includes("count") ||
    text.includes("records") ||
    text.includes("rows") ||
    text.includes("window") ||
    text.includes("seconds") ||
    text.includes("percent") ||
    text.includes("fraction") ||
    text.includes("pga") ||
    text.includes("pgv") ||
    text.includes("sa")
  );
}

function formatSheet(sheet) {
  sheet.showGridLines = false;
  const used = sheet.getUsedRange(true);
  if (!used) {
    return;
  }
  used.format.font.name = "Arial";
  used.format.font.size = 10;
  used.format.wrapText = false;
  used.format.autofitColumns();
  used.format.autofitRows();

  const values = used.values ?? [];
  if (values.length === 0) {
    return;
  }
  const colCount = values.reduce((max, row) => Math.max(max, row.length), 0);
  if (colCount === 0) {
    return;
  }
  const header = sheet.getRangeByIndexes(0, 0, 1, colCount);
  header.format.fill.color = "#EAF2F8";
  header.format.font.bold = true;
  header.format.borders = { bottom: { style: "thin", color: "#9DB7C8" } };
  sheet.freezePanes.freezeRows(1);

  for (let col = 0; col < colCount; col += 1) {
    const colRange = sheet.getRangeByIndexes(0, col, values.length, 1);
    const width = Math.min(Math.max(12, String(values[0]?.[col] ?? "").length + 2), 34);
    colRange.format.columnWidth = width;
    if (values.length > 1 && isNumberHeader(values[0]?.[col])) {
      sheet.getRangeByIndexes(1, col, values.length - 1, 1).setNumberFormat("0.000");
    }
  }
}

function writeMatrix(sheet, matrix) {
  const rowCount = matrix.length;
  const colCount = matrix.reduce((max, row) => Math.max(max, row.length), 0);
  const padded = matrix.map((row) => {
    const next = [...row];
    while (next.length < colCount) {
      next.push(null);
    }
    return next;
  });
  sheet.getRangeByIndexes(0, 0, rowCount, colCount).values = padded;
}

async function addCsvSheet(workbook, entry) {
  const abs = path.join(repoRoot, entry.source);
  const csvText = await fs.readFile(abs, "utf8");
  const imported = await Workbook.fromCSV(csvText, { sheetName: entry.sheet });
  const importedSheet = imported.worksheets.getItem(entry.sheet);
  const importedUsed = importedSheet.getUsedRange(true);
  const values = importedUsed?.values ?? [];
  const sheet = workbook.worksheets.add(entry.sheet);
  if (values.length > 0) {
    writeMatrix(sheet, values);
  }
  formatSheet(sheet);
}

async function addStatusSheet(workbook, entry) {
  const sheet = workbook.worksheets.add(entry.sheet);
  writeMatrix(sheet, [
    ["field", "value"],
    ["figure_or_table", entry.figure],
    ["status", entry.status],
    ["source_artifact", entry.source],
    ["notes", entry.notes],
    ["final_submission_action", "Build a numeric table for residual diagnostic panel values before final Nature Communications submission."],
  ]);
  formatSheet(sheet);
  sheet.getRange("B2:B6").format.wrapText = true;
  sheet.getRange("B2:B6").format.columnWidth = 105;
  sheet.getRange("A1:B6").format.autofitRows();
}

async function buildWorkbook() {
  await fs.mkdir(outputDir, { recursive: true });
  await fs.mkdir(previewDir, { recursive: true });

  const workbook = Workbook.create();
  const readme = workbook.worksheets.add("README");
  writeMatrix(readme, [
    ["NC source data package", "Cross-regional predictability limits of strong shaking from early P waves"],
    ["generated", "2026-06-20"],
    ["scope", "Derived, figure-level and supplement-level CSV tables only. Raw waveforms are not included."],
    [],
    ["sheet", "figure_or_table", "source_file", "status", "notes"],
    ...sources.map((entry) => [entry.sheet, entry.figure, entry.source, entry.status, entry.notes]),
  ]);
  formatSheet(readme);
  readme.getRange("A1:E1").format.font.bold = true;
  readme.getRange("A1:E3").format.wrapText = true;
  readme.getRange("A1:E3").format.fill.color = "#F7F9FB";
  readme.getRangeByIndexes(0, 0, 5 + sources.length, 1).format.columnWidth = 24;
  readme.getRangeByIndexes(0, 1, 5 + sources.length, 1).format.columnWidth = 38;
  readme.getRangeByIndexes(0, 2, 5 + sources.length, 1).format.columnWidth = 58;
  readme.getRangeByIndexes(0, 3, 5 + sources.length, 1).format.columnWidth = 28;
  readme.getRangeByIndexes(0, 4, 5 + sources.length, 1).format.columnWidth = 82;
  readme.getRange("A1:E20").format.autofitRows();

  for (const entry of sources) {
    if (entry.status === "included") {
      await addCsvSheet(workbook, entry);
    } else {
      await addStatusSheet(workbook, entry);
    }
  }

  const errors = await workbook.inspect({
    kind: "match",
    searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
    options: { useRegex: true, maxResults: 300 },
    summary: "final formula error scan",
    maxChars: 4000,
  });
  if (errors.ndjson.includes("#REF!") || errors.ndjson.includes("#DIV/0!") || errors.ndjson.includes("#VALUE!") || errors.ndjson.includes("#NAME?")) {
    throw new Error(`Workbook error scan found formula errors:\n${errors.ndjson}`);
  }

  const overview = await workbook.inspect({
    kind: "workbook,sheet,table",
    maxChars: 8000,
    tableMaxRows: 4,
    tableMaxCols: 6,
    tableMaxCellChars: 80,
  });
  await fs.writeFile(path.join(previewDir, "nc_source_data_inspect.ndjson"), overview.ndjson);

  for (const entry of [{ sheet: "README" }, ...sources]) {
    const blob = await workbook.render({ sheetName: entry.sheet, autoCrop: "all", scale: 1, format: "png" });
    const bytes = new Uint8Array(await blob.arrayBuffer());
    await fs.writeFile(path.join(previewDir, `${entry.sheet}.png`), bytes);
  }

  const output = await SpreadsheetFile.exportXlsx(workbook);
  await output.save(workbookPath);
  await fs.rm(`${workbookPath}.inspect.ndjson`, { force: true });

  const manifest = [
    "# NC Source Data Manifest",
    "",
    "Workbook:",
    "",
    `- \`${relPath(workbookPath)}\``,
    "",
    "Scope:",
    "",
    "- Derived figure-level and supplement-level CSV tables.",
    "- Raw waveform files are excluded.",
    "- Figure 5 residual diagnostic source data are included.",
    "",
    "| sheet | figure/table | source file | status | notes |",
    "|---|---|---|---|---|",
    ...sources.map((entry) => `| ${entry.sheet} | ${entry.figure} | \`${entry.source}\` | ${entry.status} | ${entry.notes.replaceAll("|", "/")} |`),
    "",
  ].join("\n");
  await fs.writeFile(manifestPath, manifest);

  console.log(JSON.stringify({
    workbook: relPath(workbookPath),
    manifest: relPath(manifestPath),
    preview_dir: relPath(previewDir),
    sheets: 1 + sources.length,
  }, null, 2));
}

await buildWorkbook();
