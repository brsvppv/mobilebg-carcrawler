from openpyxl.worksheet.table import Table
from openpyxl.utils import get_column_letter

def expand_table_to_fit(ws, table_name=None):
    """
    Expands the first table (or named table) in the worksheet to cover all non-empty rows and columns.
    Fixed to prevent Excel validation errors.
    """
    if not ws.tables:
        return
        
    try:
        if table_name and table_name in ws.tables:
            table = ws.tables[table_name]
        else:
            table = next(iter(ws.tables.values()))
            
        if not table:
            return
            
        # Get valid bounds
        min_col = 1
        max_col = max(ws.max_column, 1)
        min_row = 1
        max_row = max(ws.max_row, 2)  # At least 2 rows for a valid table
        
        # Create valid range
        end_col_letter = get_column_letter(max_col)
        new_range = f"A{min_row}:{end_col_letter}{max_row}"
        
        # Update table reference safely
        table.ref = new_range
        
    except Exception as e:
        # Silently fail to avoid breaking Excel export
        pass
