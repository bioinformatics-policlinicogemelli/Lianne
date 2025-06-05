import pandas as pd
from pathlib import Path
import argparse

# Valid neoplasms for check (lowercase and stripped)
valid_neoplasms = {
    "ovary", "endometrium", "lung", "colorectum", "pancreas", "prostate",
    "melanoma", "cholangiocarcinoma", "thyroid", "breast", "gist"
}

def validate_input(input_file, out_path):
    input_df = pd.read_csv(input_file, sep="\t", dtype=str)  # Everything as string for clean checking
    input_df.fillna("NA", inplace=True)  # Replace NaNs with string "NA" for consistency

    issues = []
    
    for idx, row in input_df.iterrows():
        row_issues = []

        # Check for any " NA " or cell with only whitespace
        for col in input_df.columns:
            val = row[col]
            if val.strip() == "" or val.strip().upper() == "NA":
                row_issues.append(f"Empty or NA value in column '{col}'")

            if " " in val:
                row_issues.append(f"Value in column '{col}' contains space: '{val}'")

        # Check TC values
        tc_val = row.get("TC", "").strip()
        if not tc_val.isdigit() or not (0 <= int(tc_val) <= 100):
            row_issues.append(f"Invalid TC value: '{tc_val}'")

        # Check NEOPLASM value
        neoplasm_val = row.get("NEOPLASM", "").lower().replace(" ", "")
        if neoplasm_val not in valid_neoplasms:
            row_issues.append(f"Invalid NEOPLASM value: '{row.get('NEOPLASM', '')}'")

        if row_issues:
            issues.append({
                "Row_Index": idx,
                "SampleID": row.get("SampleID", ""),
                "PatientID": row.get("PatientID", ""),
                "Issues": "; ".join(row_issues),
                "Row_Data": row.to_dict()
            })

    # Write report
    report_file = Path(out_path) / (Path(input_file).stem + "_validation_report.txt")
    with open(report_file, "w") as f:
        if not issues:
            msg = "✅ No issues found in the input file.\n"
            print(msg)
            f.write(msg)
        else:
            header = f"🚨 Found {len(issues)} problematic row(s):\n\n"
            print(header)
            f.write(header)
            for entry in issues:
                f.write(f"[Row {entry['Row_Index']}] SampleID: {entry['SampleID']}, PatientID: {entry['PatientID']}\n")
                f.write(f"Issues: {entry['Issues']}\n")
                f.write("Row Data:\n")
                for key, val in entry["Row_Data"].items():
                    f.write(f"  {key}: {val}\n")
                f.write("-" * 60 + "\n")



class MyArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise ValueError(message)


if __name__ == '__main__':
    parser = MyArgumentParser(add_help=True, exit_on_error=False, description='Validation script for input file')
    
    parser.add_argument('-i', '--input_file', required=True, help='Input file to validate')
    parser.add_argument('-o', '--out_path', required=True, help='Path to save the validation report')

    args = parser.parse_args()
    validate_input(args.input_file, args.out_path)
