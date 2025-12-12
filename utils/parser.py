import pandas as pd
import pdfplumber
import re
from datetime import datetime
import io

class MpesaParser:
    """
    Parser for M-Pesa Statements (PDF and CSV).
    """
    
    REQUIRED_COLUMNS = ['Receipt No.', 'Completion Time', 'Details', 'Transaction Status', 'Paid In', 'Withdrawn', 'Balance']
    
    @staticmethod
    def parse_file(file_obj, file_type):
        """
        Main entry point for parsing.
        
        Args:
            file_obj: The file object (BytesIO) from Streamlit uploader
            file_type: 'pdf' or 'csv'
            
        Returns:
            pd.DataFrame: Cleaned transaction data
        """
        try:
            if file_type.lower() == 'pdf':
                return MpesaParser.parse_pdf(file_obj)
            elif file_type.lower() == 'csv':
                return MpesaParser.parse_csv(file_obj)
            else:
                raise ValueError("Unsupported file format. Please upload PDF or CSV.")
        except Exception as e:
            raise Exception(f"Error parsing file: {str(e)}")

    @staticmethod
    def parse_csv(file_obj):
        """Parses CSV M-Pesa statement."""
        try:
            # Try reading with different parameters as M-Pesa CSVs can be messy
            # Sometimes they have meta-data in first few rows
            df = pd.read_csv(file_obj)
            
            # If the required columns aren't in the header, search for the header row
            if not all(col in df.columns for col in MpesaParser.REQUIRED_COLUMNS):
                # Reload looking for the header
                file_obj.seek(0)
                # Read first 20 lines to find header
                content = file_obj.read().decode('utf-8', errors='ignore').splitlines()
                header_row = -1
                for i, line in enumerate(content[:20]):
                    if "Receipt No." in line and "Completion Time" in line:
                        header_row = i
                        break
                
                if header_row != -1:
                    file_obj.seek(0)
                    df = pd.read_csv(file_obj, skiprows=header_row)
                else:
                    raise ValueError("Could not likely find M-Pesa transaction headers in CSV.")

            return MpesaParser._clean_data(df)
            
        except Exception as e:
            raise ValueError(f"CSV Parsing failed: {str(e)}")

    @staticmethod
    def parse_pdf(file_obj):
        """Parses PDF M-Pesa statement using pdfplumber."""
        transactions = []
        
        try:
            with pdfplumber.open(file_obj) as pdf:
                for page in pdf.pages:
                    # Extract tables
                    tables = page.extract_tables()
                    
                    for table in tables:
                        # Check if table looks like transaction list
                        # M-Pesa tables usually have 7-8 columns
                        # We look for a row with headers or data that looks like headers
                        
                        if not table:
                            continue
                            
                        # Convert to dataframe to easy manipulation
                        df_table = pd.DataFrame(table)
                        
                        # Find header row
                        header_idx = -1
                        for idx, row in df_table.iterrows():
                            # Join row values and check for key headers
                            row_str = " ".join([str(x) for x in row if x]).lower()
                            if "receipt" in row_str and "details" in row_str and "balance" in row_str:
                                header_idx = idx
                                break
                        
                        if header_idx != -1:
                            # Set headers
                            headers = df_table.iloc[header_idx]
                            # Clean headers (handle newlines etc)
                            headers = [str(h).replace('\n', ' ').strip() for h in headers]
                            
                            # Get data
                            data = df_table.iloc[header_idx+1:]
                            if not data.empty:
                                data.columns = headers
                                # Filter rows that are actual transactions (have Receipt No)
                                # Assuming 'Receipt No.' is usually the first or second column
                                # We'll just standardize columns mapping
                                
                                # Map found columns to standard ones if possible
                                # This is a simplification; robust mapping might be needed
                                transactions.append(data)

            if not transactions:
                raise ValueError("No transaction tables found in PDF.")
                
            # Concatenate all parts
            full_df = pd.concat(transactions, ignore_index=True)
            
            return MpesaParser._clean_data(full_df)

        except Exception as e:
            raise ValueError(f"PDF Parsing failed: {str(e)}")

    @staticmethod
    def _clean_data(df):
        """Standardizes and cleans the dataframe."""
        
        # Standardize column names (basic normalization)
        df.columns = [c.strip().replace('\n', ' ') for c in df.columns]
        
        # Ensure we have required columns. Partial matching.
        # Map: Receipt No., Completion Time, Details, Transaction Status, Paid In, Withdrawn, Balance
        # Sometimes PDF headers are slightly different.
        
        col_map = {}
        for col in df.columns:
            l_col = col.lower()
            if 'receipt' in l_col: col_map[col] = 'Receipt No.'
            elif 'time' in l_col or 'date' in l_col: col_map[col] = 'Completion Time'
            elif 'details' in l_col: col_map[col] = 'Details'
            elif 'status' in l_col: col_map[col] = 'Transaction Status'
            elif 'paid in' in l_col: col_map[col] = 'Paid In'
            elif 'withdrawn' in l_col: col_map[col] = 'Withdrawn'
            elif 'balance' in l_col: col_map[col] = 'Balance'
            
        df = df.rename(columns=col_map)
        
        # Drop rows where Receipt No. is missing (footer garbage)
        if 'Receipt No.' in df.columns:
            df = df.dropna(subset=['Receipt No.'])
            df = df[df['Receipt No.'].astype(str).str.len() > 5] # Basic filter
        
        # Helper to clean numbers
        def clean_currency(val):
            if pd.isna(val) or val == '': return 0.0
            val = str(val).replace(',', '').replace(' ', '')
            # Remove negative signs if present in strings, we handle logic by column
            val = val.replace('-', '') 
            try:
                return float(val)
            except:
                return 0.0

        # Clean numeric columns
        for col in ['Paid In', 'Withdrawn', 'Balance']:
            if col in df.columns:
                df[col] = df[col].apply(clean_currency)
            else:
                df[col] = 0.0 # Default if missing
        
        # Calculate 'Amount' and 'Type'
        # Expenses are 'Withdrawn', Income is 'Paid In'
        # We want a single signed 'Amount' column? Or keep separate?
        # User wants: Income, Expense differentiation.
        
        df['Amount'] = df.apply(lambda row: row['Paid In'] if row['Paid In'] > 0 else -row['Withdrawn'], axis=1)
        
        # Parse Dates
        if 'Completion Time' in df.columns:
            # Common formats: "2023-10-27 14:30:00" or "27-10-2023 14:30:00"
            df['Completion Time'] = pd.to_datetime(df['Completion Time'], errors='coerce')
        
        # Categorization based on 'Details'
        df['Category'] = df['Details'].apply(MpesaParser._categorize_transaction)
        
        return df

    @staticmethod
    def _categorize_transaction(details):
        """Simple rule-based categorization."""
        details = str(details).lower()
        
        if 'airtime' in details: return 'Airtime'
        if 'pay bill' in details or 'paybill' in details: return 'Pay Bill'
        if 'buy goods' in details: return 'Buy Goods'
        if 'customer transfer' in details or 'sent to' in details: return 'Sent to M-Pesa' # Logic might need refinement based on exact text
        if 'received from' in details: return 'Received M-Pesa'
        if 'withdraw' in details: return 'Withdraw Cash'
        if 'deposit' in details: return 'Deposit'
        if 'loan' in details or 'fuliza' in details or 'm-shwari' in details: return 'Loan'
        
        return 'Other'
