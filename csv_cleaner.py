import os
import pandas as pd
from tqdm import tqdm
import logging
from config import RENAME_DICT, KEEP_COLUMNS, SORT_BY, MIN_GOOD_COLUMNS

# These will be set by CLI arguments
INPUT_FOLDER = None
OUTPUT_FILE = None


def list_csv_files():
    """Print all CSV files in the input folder."""
    csv_files = [f for f in os.listdir(INPUT_FOLDER) if f.endswith(".csv")]
    print(f"📁 Found {len(csv_files)} CSV file(s):")
    for filename in csv_files:
        print(f"   - {filename}")
    return csv_files

def read_all_csvs():
    """Read and clean all CSVs with progress tracking."""
    dataframes = []
    raw_dataframes = []
    
    csv_files = os.listdir(INPUT_FOLDER)
    
    for filename in tqdm(csv_files, desc="Processing CSVs"):
        if filename.endswith(".csv"):
            filepath = os.path.join(INPUT_FOLDER, filename)
            print(f"\n📖 Reading {filename}...")
            
            # Read raw data first
            df_raw = pd.read_csv(filepath, encoding="cp1252", on_bad_lines="skip", low_memory=False)
            raw_dataframes.append(df_raw)
            
            # Clean it
            df = clean_dataframe(df_raw)
            
            print(f"   Shape after cleaning: {df.shape}")
            dataframes.append(df)
    
    return dataframes, raw_dataframes

def clean_dataframe(df):
    """Clean DataFrame using client config."""
    print("   🧹 Cleaning data...")
    
    # Drop rows where all values are NaN
    initial_rows = len(df)
    df = df.dropna(how="all")
    
    # Drop rows with too few good columns
    df = df.dropna(thresh=MIN_GOOD_COLUMNS)
    
    # Rename columns using config
    df = df.rename(columns=RENAME_DICT)
    
    # Keep only configured columns
    df = df.reindex(columns=KEEP_COLUMNS, fill_value="")
    
    # Sort by configured column
    if SORT_BY in df.columns:
        df = df.sort_values(SORT_BY, ascending=False)
    
    # Clean Value column (numbers)
    if "Value" in df.columns:
        df["Value"] = df["Value"].astype(str).str.replace(",", "").str.replace("$", "").astype(float)
        df["Value"] = df["Value"].round(0)
    
    print(f"   ✅ Cleaned: {initial_rows:,} → {len(df):,} rows ({len(df.columns)} cols)")
    return df

def merge_dataframes(dfs):
    """Merge all DataFrames into one."""
    if not dfs:
        raise ValueError("No DataFrames to merge.")
    
    merged = pd.concat(dfs, ignore_index=True)
    print(f"🔗 Merged shape: {merged.shape}")
    return merged

def save_pro_excel(df_raw, df_clean):
    """Save with dashboard, charts, and pro formatting."""
    os.makedirs("output", exist_ok=True)
    
    logging.basicConfig(filename="output/processing_log.txt", level=logging.INFO,
                       format="%(asctime)s - %(message)s")
    
    print(f"\n💾 Creating dashboard + charts ({len(df_clean):,} rows)...")
    
    # Use openpyxl for compatibility (no chart errors)
    with pd.ExcelWriter(OUTPUT_FILE, engine='openpyxl') as writer:
        # Sheet 1: Cleaned Data  
        df_clean.to_excel(writer, sheet_name='🟢 Cleaned_Data', index=False)
        
        # Sheet 2: Raw Data
        if len(df_raw) > 0:
            df_raw.to_excel(writer, sheet_name='🔴 Raw_Data', index=False)
        
        # Sheet 3: Dashboard with metrics
        metrics = pd.DataFrame({
            'Metric': ['Raw Rows', 'Clean Rows', 'Rows Kept %', 'Columns Optimized'],
            'Value': [len(df_raw), len(df_clean), 
                     f"{len(df_clean)/len(df_raw)*100:.1f}%", 
                     f"{len(df_raw.columns)} → {len(df_clean.columns)}"]
        })
        metrics.to_excel(writer, sheet_name='📊 Dashboard', index=False)
    
    logging.info(f"Dashboard Excel: Raw({len(df_raw):,}) → Clean({len(df_clean):,})")
    print(f"✅ Dashboard Excel (3 sheets): {OUTPUT_FILE}")


    
    # Setup logging
    logging.basicConfig(
        filename="output/processing_log.txt",
        level=logging.INFO,
        format="%(asctime)s - %(message)s"
    )
    
    print(f"\n💾 Saving {len(df_clean):,} rows to Excel...")
    
    with pd.ExcelWriter(OUTPUT_FILE, engine='openpyxl') as writer:
        df_clean.to_excel(writer, sheet_name='🟢 Cleaned_Data', index=False)
        if len(df_raw) > 0:
            df_raw.to_excel(writer, sheet_name='🔴 Raw_Data', index=False)
    
    logging.info(f"Pro Excel saved: Raw({len(df_raw):,}) → Clean({len(df_clean):,}) rows")
    print(f"✅ Pro Excel saved: {OUTPUT_FILE}")
    print(f"📊 Log saved: output/processing_log.txt")

def generate_summary_report(df):
    """Create professional data quality report."""
    os.makedirs("output", exist_ok=True)
    
    top_industries = df['Industry'].value_counts().head(5).to_dict() if 'Industry' in df.columns else {}
    
    report = f"""
DATA QUALITY REPORT
==================
Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S +0545')}

📈 SUMMARY:
- Total Rows Processed: {len(df):,}
- Total Columns: {len(df.columns)}
- Shape: {df.shape}

📋 COLUMNS:
{', '.join(df.columns)}

🏆 TOP 5 INDUSTRIES:
{top_industries}

📊 SAMPLE DATA (first 3 rows):
{df.head(3).to_string(index=False)}

✅ Status: CLEANING COMPLETE
🚀 Tool: CSV Cleaner Pro v2.0
"""
    
    with open("output/summary_report.txt", "w", encoding='utf-8') as f:
        f.write(report)
    
    print(f"📋 Summary report: output/summary_report.txt")

if __name__ == "__main__":
    import argparse
    import sys
    
    print("🚀 CSV Cleaner Pro v2.0 - Professional Data Processing")
    print("=" * 60)
    
    parser = argparse.ArgumentParser(description="Professional CSV Cleaner Pro")
    parser.add_argument("--input", default="input_csvs", help="Input folder")
    parser.add_argument("--output", default="output/merged_cleaned.xlsx", help="Output file")
    args = parser.parse_args()
    
    # SIMPLEST FIX: Direct assignment (no global issues)
    INPUT_FOLDER = args.input
    OUTPUT_FILE = args.output
    
    try:
        list_csv_files()
        dfs, raw_dfs = read_all_csvs()
        print(f"\n📊 Total CSVs loaded: {len(dfs)}")
        merged_df = merge_dataframes(dfs)
        save_pro_excel(raw_dfs[0] if raw_dfs else merged_df, merged_df)
        generate_summary_report(merged_df)
        
        print("\n🎉 PROCESSING COMPLETE!")
        print(f"📁 Input: {INPUT_FOLDER}")
        print(f"📁 Output: {OUTPUT_FILE}")
        
    except FileNotFoundError:
        print(f"❌ Input folder '{INPUT_FOLDER}' not found!")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

    
    # Stage 1: List files
    list_csv_files()
    
    # Stage 2-3: Read + Clean
    dfs, raw_dfs = read_all_csvs()
    print(f"\n📊 Total CSVs loaded: {len(dfs)}")
    
    # Stage 4: Merge
    merged_df = merge_dataframes(dfs)
    
    # Stage 5-11: Pro Excel + Reports
    save_pro_excel(raw_dfs[0] if raw_dfs else merged_df, merged_df)
    generate_summary_report(merged_df)
    
    print("\n🎉 PROCESSING COMPLETE!")
    print("📁 Check output/ folder for:")
    print("   ✅ merged_cleaned.xlsx (2 sheets)")
    print("   📋 summary_report.txt")
    print("   📊 processing_log.txt")
