# config.py - Client customizes this file only

# Column renaming (add your client's columns here)
RENAME_DICT = {
    "description": "Description",
    "industry": "Industry", 
    "level": "Level",
    "size": "Employee_Size",
    "line_code": "Line_Code",
    "value": "Value",
    "Unit": "Unit",
    "Footnotes": "Footnotes"
}

# Columns to KEEP (only these will be in final Excel)
KEEP_COLUMNS = ["Description", "Industry", "Level", "Employee_Size", "Value", "Unit"]

# Sort by this column (descending)
SORT_BY = "Value"

# Minimum good columns per row (drops junk rows)
MIN_GOOD_COLUMNS = 5
