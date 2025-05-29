import pandas as pd
from pathlib import Path

# Fixed run_id path
run_id_path = "/data/data_storage/novaseq_results/Dragen_2.5/250110_A01423_0282_AH2H5NDMX2_v2_5"
run_id = Path(run_id_path).name  # Extract just the folder name

# Load input file
input_file = Path("input_file_alessia.txt")
input_df = pd.read_csv(input_file, sep="\t")

# Replace spaces in column names and string values
input_df.columns = input_df.columns.str.replace(" ", "_")
input_df = input_df.applymap(lambda x: x.replace(" ", "_") if isinstance(x, str) else x)

# Map NEOPLASM to ONCOTREE_CODE
neoplasm_to_oncotree = {
    "Ovary": "OVARY",
    "Endometrium": "UTERUS",
    "Lung": "NSCLC",
    "Colorectum": "BOWEL",
    "Pancreas": "PANCREAS",
    "Prostate": "PROSTATE",
    "Melanoma": "MELANOMA",
    "Cholangiocarcinoma": "BILIARY_TRACT",
    "Thyroid": "THYROID",
    "Breast": "BREAST",
    "GIST": "GIST"
}
input_df["ONCOTREE_CODE"] = input_df["NEOPLASM"].map(neoplasm_to_oncotree).fillna("")

# Define base path
run_path = Path("/data/data_storage/novaseq_results/Dragen_2.5")

# Path builder functions
def build_snv_path(run_id, patient_id, sample_id):
    return run_path / run_id / "Results" / str(patient_id) / str(sample_id) / f"{sample_id}_MergedSmallVariants.genome.vcf"

def build_cnv_path(run_id, patient_id, sample_id):
    return run_path / run_id / "Results" / str(patient_id) / str(sample_id) / f"{sample_id}.cnv.vcf"

def build_comb_path(run_id, patient_id):
    return run_path / run_id / "Results" / str(patient_id) / f"{patient_id}_CombinedVariantOutput.tsv"

# Collect rows and missing paths
output_rows = []
missing_paths = []

for _, row in input_df.iterrows():
    sample_id = row["SampleID"]
    patient_id = row["PatientID"]

    snv = build_snv_path(run_id, patient_id, sample_id)
    cnv = build_cnv_path(run_id, patient_id, sample_id)
    comb = build_comb_path(run_id, patient_id)

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
        "NEOPLASM": row.get("NEOPLASM", ""),
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
output_file_name = input_file.stem + "_data_varan.tsv"
output_path = Path("/data/data_storage/novaseq_results/research/CbioPortal/Input_file/file_input") / output_file_name

output_df = pd.DataFrame(output_rows)
output_df.to_csv(output_path, sep="\t", index=False)

# Print summary of missing paths
if missing_paths:
    print("\n🚫 Missing files for the following samples:\n")
    for entry in missing_paths:
        sample = entry["sample"]
        snv, cnv, comb = entry["paths"]
        print(f"[{sample}]")
        print(f"  ❌ SNV:  {snv}" if entry["missing_snv"] else f"  ✅ SNV:  {snv}")
        print(f"  ❌ CNV:  {cnv}" if entry["missing_cnv"] else f"  ✅ CNV:  {cnv}")
        print(f"  ❌ COMB: {comb}" if entry["missing_comb"] else f"  ✅ COMB: {comb}")
        print("-" * 60)
else:
    print("✅ All paths exist for all samples!")
