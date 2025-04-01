import pandas as pd

def convert_xlsx_to_csv(xlsx_file_path, csv_file_path):
    """
    Convert an Excel (.xlsx) file to a CSV file.

    :param xlsx_file_path: Path to the input .xlsx file.
    :param csv_file_path: Path to the output .csv file.
    """
    try:
        # Read the Excel file
        df = pd.read_excel(xlsx_file_path, engine="openpyxl")

        # Write the DataFrame to a CSV file
        df.to_csv(csv_file_path, index=False)

        print(f"Successfully converted {xlsx_file_path} to {csv_file_path}")
    except Exception as e:
        print(f"Error converting {xlsx_file_path} to CSV: {e}")

if __name__ == "__main__":
    # Input .xlsx file path
    xlsx_file_path = r"dataset.xlsx"

    # Output .csv file path
    csv_file_path = r"dataset.csv"

    # Convert the file
    convert_xlsx_to_csv(xlsx_file_path, csv_file_path)