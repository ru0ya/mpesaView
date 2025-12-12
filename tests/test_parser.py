import pytest
import pandas as pd
from io import BytesIO
from utils.parser import MpesaParser

def test_parse_csv_valid():
    csv_data = """Receipt No.,Completion Time,Details,Transaction Status,Paid In,Withdrawn,Balance
RC12345,2023-10-01 10:00:00,Buy Goods Store X,Completed,,500.00,1000.00
RC12346,2023-10-02 12:00:00,Received for Art,Completed,2000.00,,3000.00
"""
    file_obj = BytesIO(csv_data.encode('utf-8'))
    # Pandas read_csv expects bytes or string buffer. 
    # MpesaParser.parse_csv expects a file-like object that behaves like what st.file_uploader returns (BytesIO usually, but StringIO works for pandas text)
    # Let's mock it properly as BytesIO if we were using it, but pd.read_csv accepts StringIO.
    
    # We need to seek(0) in the parser, so make sure StringIO supports it.
    file_obj.seek(0)
    
    df = MpesaParser.parse_csv(file_obj)
    
    assert len(df) == 2
    assert df.iloc[0]['Receipt No.'] == 'RC12345'
    assert df.iloc[0]['Amount'] == -500.00
    assert df.iloc[1]['Amount'] == 2000.00
    assert df.iloc[0]['Category'] == 'Buy Goods'

def test_categorization():
    assert MpesaParser._categorize_transaction("Pay Bill via 12345") == "Pay Bill"
    assert MpesaParser._categorize_transaction("Sent to 0712...") == "Sent to M-Pesa"
    assert MpesaParser._categorize_transaction("Funds Received from ...") == "Received M-Pesa"
