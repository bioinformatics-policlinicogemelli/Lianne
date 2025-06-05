import pandas as pd
from pathlib import Path
import argparse

# Path builder functions
def build_snv_path(run_id_path, patient_id, sample_id):
    return run_id_path / "Results" / patient_id / sample_id / f"{sample_id}.hard-filtered.vcf"

def build_cnv_path(run_id_path, patient_id, sample_id):
    return run_id_path / "Results" / patient_id / sample_id / f"{sample_id}.cnv.vcf"

def build_comb_path(run_id_path,  patient_id):
    return run_id_path / "Results" / patient_id / f"{patient_id}_CombinedVariantOutput.tsv"

def reorganize_input(run_id_path, input_file, out_path):

    # Fixed run_id path
    run_id_path = Path(run_id_path)
    run_id = run_id_path.name  # Extract just the folder name

    # Load input file
    #input_file = Path("input_file_alessia.txt")
    input_df = pd.read_csv(input_file, sep="\t", dtype={"SampleID": str, "PatientID": str})


    # Replace spaces in column names and string values
    input_df.columns = input_df.columns.str.replace(" ", "_")
    input_df = input_df.applymap(lambda x: x.replace(" ", "_") if isinstance(x, str) else x)
    input_df["NEOPLASM_CLEAN"] = input_df["NEOPLASM"].str.lower().str.replace(" ", "", regex=False)

    # Filter out rows with 'RNA' in SampleID (case-insensitive just in case)
    input_df = input_df[~input_df["SampleID"].str.contains("RNA", case=False, na=False)]


    # Map NEOPLASM to ONCOTREE_CODE
    neoplasm_to_oncotree = {
        "ovary": "OVARY",
        "endometrium": "UTERUS",
        "lung": "NSCLC",
        "colorectum": "BOWEL",
        "pancreas": "PANCREAS",
        "prostate": "PROSTATE",
        "melanoma": "MELANOMA",
        "cholangiocarcinoma": "BILIARY_TRACT",
        "thyroid": "THYROID",
        "breast": "BREAST",
        "gist": "GIST"
    }

    input_df["ONCOTREE_CODE"] = input_df["NEOPLASM_CLEAN"].map(neoplasm_to_oncotree).fillna("")

    # Define base path
    #run_path = Path("/data/data_storage/novaseq_results/Dragen_2.5")


    # Collect rows and missing paths
    output_rows = []
    missing_paths = []

    for _, row in input_df.iterrows():
        sample_id = row["SampleID"]
        patient_id = row["PatientID"]

        snv = build_snv_path(run_id_path, patient_id, sample_id)
        cnv = build_cnv_path(run_id_path, patient_id, sample_id)
        comb = build_comb_path(run_id_path, patient_id)

        # Record any missing paths
        missing_info = {
            "sample": sample_id,
            "missing_snv": not snv.exists(),
            "missing_cnv": not cnv.exists(),
            "missing_comb": not comb.exists(),
            "paths": (snv, cnv, comb)
        }
        if any([missing_info["missing_snv"], missing_info["missing_cnv"], missing_info["missing_comb"]]):
            missing_paths.append(missing_info)

        # Append row (include paths as strings)
        output_rows.append({
            "SAMPLE_ID": sample_id,
            "PATIENT_ID": patient_id,
            "RUN_ID": run_id,
            "ONCOTREE_CODE": row.get("ONCOTREE_CODE", ""),
            "NEOPLASM": row.get("NEOPLASM_CLEAN", ""),
            "ALIAS": row.get("ALIAS", ""),
            "snv_path": str(snv),
            "cnv_path": str(cnv),
            "comb_path": str(comb),
            "TC": row.get("TC", ""),
            "MSI": "",
            "TMB": "",
            "MSI_THR": "",
            "TMB_THR": ""
        })

    # Save output file
    output_file_name = run_id + "_data_varan.tsv"
    output_path = Path(out_path) / output_file_name

    output_df = pd.DataFrame(output_rows)
    output_df.to_csv(output_path, sep="\t", index=False)

    warning_file = Path(out_path) / f"{run_id}_missing_paths.txt"

    with open(warning_file, "w") as f:
        if missing_paths:
            header = "\n🚫 Missing files for the following samples:\n"
            f.write(header + "\n")

            for entry in missing_paths:
                sample = entry["sample"]
                snv, cnv, comb = entry["paths"]

                snv_line = f"  ❌ SNV:  {snv}" if entry["missing_snv"] else f"  ✅ SNV:  {snv}"
                cnv_line = f"  ❌ CNV:  {cnv}" if entry["missing_cnv"] else f"  ✅ CNV:  {cnv}"
                comb_line = f"  ❌ COMB: {comb}" if entry["missing_comb"] else f"  ✅ COMB: {comb}"


                f.write(f"[{sample}]\n")
                f.write(snv_line + "\n")
                f.write(cnv_line + "\n")
                f.write(comb_line + "\n")
                f.write("-" * 60 + "\n")
        else:
            success_msg = "✅ All paths exist for all samples!"
            f.write(success_msg + "\n")


class MyArgumentParser(argparse.ArgumentParser):
  """An argument parser that raises an error, instead of quits"""
  def error(self, message):
    raise ValueError(message)


if __name__ == '__main__':
    parser = MyArgumentParser(add_help=True, exit_on_error=False, usage=None, description='Argument of Varan script')
    

    parser.add_argument('-i', '--input_file', required=True, 
                        help='input file')
    

    parser.add_argument('-r', '--run_path', required=True, 
                        help='run path')
    

    parser.add_argument('-o', '--out_path', required=True, 
                        help='output path')
    
    args = parser.parse_args()

    reorganize_input(args.run_path, args.input_file, args.out_path)