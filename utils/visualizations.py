import plotly.express as px
import plotly.graph_objects as go
from config.settings import THEME_COLORS

class Charts:
    """
    Generates Plotly charts for M-Pesa Analysis.
    """
    
    @staticmethod
    def get_income_expense_pie(kpis):
        """
        Generates a pie chart for Income vs Expenses.
        """
        labels = ['Income', 'Expenses']
        values = [kpis['total_income'], kpis['total_expenses']]
        
        fig = px.pie(
            names=labels, 
            values=values, 
            hole=0.4,
            color_discrete_sequence=[THEME_COLORS[0], THEME_COLORS[1]]
        )
        fig.update_layout(
            title="Income vs Expenses",
            margin=dict(t=30, b=0, l=0, r=0)
        )
        return fig

    @staticmethod
    def get_category_bar(df):
        """
        Generates a bar chart for expenses by category.
        """
        fig = px.bar(
            df, 
            x='Amount', 
            y='Category', 
            orientation='h',
            text='Amount',
            color='Amount',
            color_continuous_scale='Reds',
            title="Expenses by Category"
        )
        fig.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            margin=dict(t=30, b=0, l=0, r=0),
            showlegend=False
        )
        fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
        return fig

    @staticmethod
    def get_monthly_trend_line(monthly_df):
        """
        Generates a line chart for monthly trends.
        """
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=monthly_df['Month'], 
            y=monthly_df['Income'],
            mode='lines+markers',
            name='Income',
            line=dict(color=THEME_COLORS[0], width=3)
        ))
        
        fig.add_trace(go.Scatter(
            x=monthly_df['Month'], 
            y=monthly_df['Expense'],
            mode='lines+markers',
            name='Expense',
            line=dict(color=THEME_COLORS[1], width=3)
        ))
        
        fig.update_layout(
            title="Monthly Income & Expense Trends",
            xaxis_title="Month",
            yaxis_title="Amount (KES)",
            hovermode="x unified",
            margin=dict(t=30, b=0, l=0, r=0),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        return fig
    
    @staticmethod
    def get_daily_activity_heatmap(df):
        """
        Generates a heatmap of transaction activity by Day of Week and Hour.
        """
        df = df.copy()
        df['DayOfWeek'] = df['Completion Time'].dt.day_name()
        df['Hour'] = df['Completion Time'].dt.hour
        
        # Order days
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        # Group
        heatmap_data = df.groupby(['DayOfWeek', 'Hour']).size().reset_index(name='Count')
        
        # Pivot for heatmap matrix
        matrix = heatmap_data.pivot(index='DayOfWeek', columns='Hour', values='Count').fillna(0)
        matrix = matrix.reindex(days_order)
        
        fig = px.imshow(
            matrix,
            labels=dict(x="Hour of Day", y="Day of Week", color="Transactions"),
            x=list(range(24)),
            y=days_order,
            color_continuous_scale="Viridis",
            aspect="auto"
        )
        fig.update_layout(title="Transaction Activity Heatmap")
        return fig
