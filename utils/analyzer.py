import pandas as pd

class ExpenseAnalyzer:
    """
    Analyzes M-Pesa transaction data.
    """
    
    @staticmethod
    def calculate_kpis(df):
        """
        Calculates Key Performance Indicators.
        """
        # Income: Positive amounts
        incident_in = df[df['Amount'] > 0]['Amount'].sum()
        
        # Expenses: Negative amounts (sum is negative, so we abs it for display usually, 
        # but here we might want to keep native or return abs. Let's return abs for 'Total Expenses')
        incident_out = df[df['Amount'] < 0]['Amount'].sum()
        
        # Net Savings / Balance Flow
        net = incident_in + incident_out # out is negative
        
        count = len(df)
        
        return {
            "total_income": incident_in,
            "total_expenses": abs(incident_out),
            "net_savings": net,
            "transaction_count": count
        }
    
    @staticmethod
    def get_category_breakdown(df, transaction_type='Expense'):
        """
        Returns category breakdown for Income or Expense.
        Args:
            transaction_type: 'Income' or 'Expense'
        """
        if transaction_type == 'Expense':
            # Filter for expenses (negative amount)
            filtered = df[df['Amount'] < 0].copy()
            filtered['Amount'] = filtered['Amount'].abs()
        else:
            # Filter for income
            filtered = df[df['Amount'] > 0].copy()
            
        return filtered.groupby('Category')['Amount'].sum().reset_index().sort_values('Amount', ascending=False)
        
    @staticmethod
    def get_monthly_trends(df):
        """
        Resamples data by month for Income and Expense.
        """
        # Ensure we have datetime index or column
        df = df.copy()
        if not pd.api.types.is_datetime64_any_dtype(df['Completion Time']):
             df['Completion Time'] = pd.to_datetime(df['Completion Time'])
             
        df.set_index('Completion Time', inplace=True)
        
        # Resample
        monthly = df.resample('M')['Amount'].agg(
            Income=lambda x: x[x > 0].sum(),
            Expense=lambda x: abs(x[x < 0].sum())
        ).reset_index()
        
        # Format month name
        monthly['Month'] = monthly['Completion Time'].dt.strftime('%b %Y')
        return monthly

    @staticmethod
    def get_top_merchants(df, n=5):
        """
        Returns top recipients/merchants by expense volume.
        We deduce merchant/recipient from 'Details'.
        This might overlap with Category if we aren't careful, 
        but extracting exact name is hard without complex regex.
        We'll use 'Details' column directly for now.
        """
        expenses = df[df['Amount'] < 0].copy()
        expenses['Amount'] = expenses['Amount'].abs()
        
        # Group by Details
        return expenses.groupby('Details')['Amount'].sum().reset_index().sort_values('Amount', ascending=False).head(n)
