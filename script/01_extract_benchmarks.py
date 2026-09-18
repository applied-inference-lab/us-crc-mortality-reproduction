"""
Extract author published benchmark tables from supplementary DOCX and XLSX files
into clean CSV files under data/benchmarks/.
"""

import os
import csv
import zipfile
import xml.etree.ElementTree as ET

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
BENCHMARK_DIR = os.path.join(BASE_DIR, "data", "benchmarks")

os.makedirs(BENCHMARK_DIR, exist_ok=True)


def extract_xlsx_sheets(xlsx_path):
    """Extract all sheets from XLSX using standard library zipfile and XML."""
    ns = {"main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    with zipfile.ZipFile(xlsx_path, "r") as z:
        # 1. Read shared strings
        shared_strings = []
        if "xl/sharedStrings.xml" in z.namelist():
            ss_tree = ET.fromstring(z.read("xl/sharedStrings.xml"))
            for si in ss_tree.findall(".//main:si", ns):
                t = si.find(".//main:t", ns)
                shared_strings.append(t.text if t is not None else "")

        # 2. Read workbook to map rId to sheet name
        wb_tree = ET.fromstring(z.read("xl/workbook.xml"))
        rels_tree = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
        rel_ns = {"rel": "http://schemas.openxmlformats.org/package/2006/relationships"}
        id_to_target = {r.attrib["Id"]: r.attrib["Target"] for r in rels_tree.findall(".//rel:Relationship", rel_ns)}

        sheets = {}
        for s in wb_tree.findall(".//main:sheet", ns):
            s_name = s.attrib["name"]
            r_id = s.attrib["{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"]
            target = id_to_target[r_id]
            if not target.startswith("xl/"):
                target = "xl/" + target.lstrip("/")

            # Read worksheet
            ws_tree = ET.fromstring(z.read(target))
            rows_data = []
            for r in ws_tree.findall(".//main:row", ns):
                row_vals = []
                for c in r.findall("main:c", ns):
                    v = c.find("main:v", ns)
                    val = v.text if v is not None else ""
                    if c.attrib.get("t") == "s" and val.isdigit():
                        idx = int(val)
                        val = shared_strings[idx] if idx < len(shared_strings) else ""
                    row_vals.append(val)
                if any(row_vals):
                    rows_data.append(row_vals)
            sheets[s_name] = rows_data
    return sheets


def extract_docx_tables(docx_path):
    """Extract tables from DOCX using standard library zipfile and XML."""
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    with zipfile.ZipFile(docx_path, "r") as z:
        tree = ET.fromstring(z.read("word/document.xml"))
        tables = []
        for tbl in tree.findall(".//w:tbl", ns):
            table_data = []
            for row in tbl.findall(".//w:tr", ns):
                row_data = []
                for cell in row.findall(".//w:tc", ns):
                    texts = [t.text for t in cell.findall(".//w:t", ns) if t.text]
                    cell_text = "".join(texts).strip()
                    row_data.append(cell_text)
                if any(row_data):
                    table_data.append(row_data)
            if table_data:
                tables.append(table_data)
    return tables


def main():
    print("=== Extracting XLSX Benchmarks ===")
    xlsx_path = os.path.join(RAW_DIR, "supplement_table3_arima_and_forecasts.xlsx")
    sheets = extract_xlsx_sheets(xlsx_path)

    # eTable 4
    if "eTable 4" in sheets:
        etable4_rows = sheets["eTable 4"]
        out_path = os.path.join(BENCHMARK_DIR, "etable4_arima_specifications.csv")
        with open(out_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(etable4_rows)
        print(f"Saved eTable 4 ({len(etable4_rows)} rows) -> {out_path}")

    # eTable 5
    if "eTable 5" in sheets:
        etable5_rows = sheets["eTable 5"]
        out_path = os.path.join(BENCHMARK_DIR, "etable5_annual_forecasts_2024_2040.csv")
        with open(out_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(etable5_rows)
        print(f"Saved eTable 5 ({len(etable5_rows)} rows) -> {out_path}")

    print("\n=== Extracting DOCX Benchmarks ===")
    docx_path = os.path.join(RAW_DIR, "supplement_table2_observed_and_joinpoint.docx")
    docx_tables = extract_docx_tables(docx_path)
    print(f"Found {len(docx_tables)} tables in supplement_table2.docx")

    table_names = [
        "etable1_observed_nonmetastatic_mortality.csv",
        "etable2_joinpoint_models.csv",
        "etable3_prepandemic_sensitivity_models.csv"
    ]

    for idx, table_data in enumerate(docx_tables):
        fname = table_names[idx] if idx < len(table_names) else f"table_{idx+1}.csv"
        out_path = os.path.join(BENCHMARK_DIR, fname)
        with open(out_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(table_data)
        print(f"Saved Table {idx+1} ({len(table_data)} rows) -> {out_path}")


if __name__ == "__main__":
    main()
