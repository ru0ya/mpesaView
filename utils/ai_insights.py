import os
import google.generativeai as genai
from config.settings import GEMINI_API_KEY
import json

class FinancialAdvisor:
    """
    Integrates with Google Gemini to provide financial insights.
    """
    
    def __init__(self, api_key=None, model_name='gemini-2.0-flash'):
        self.api_key = api_key if api_key else GEMINI_API_KEY
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(model_name)
        else:
            self.model = None

    @staticmethod
    def list_available_models(api_key):
        """
        Lists available Gemini models that support content generation.
        """
        if not api_key: return []
        try:
            genai.configure(api_key=api_key)
            models = []
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    models.append(m.name.replace('models/', ''))
            return sorted(models)
        except:
            return []

    def generate_insights(self, kpis, top_categories, monthly_trend=None):
        """
        Generates insights based on financial data.
        """
        if not self.model:
            return "⚠️ Gemini API Key not found. Please set `GEMINI_API_KEY` in your .env file to enable AI insights."

        # Prepare context data
        context = {
            "period_summary": kpis,
            "top_spending_categories": top_categories.head(5).to_dict('records') # Take top 5
        }
        
        # Construct Prompt
        prompt = f"""
        You are an expert financial advisor analyzing M-Pesa transaction data.
        
        Financial Summary:
        {json.dumps(context, indent=2, default=str)}
        
        Please provide a professional financial assessment including:
        1. **Spending Analysis**: A concise summary of where the money is going.
        2. **Actionable Recommendations**: 3-5 specific tips to improve financial health or reduce expenses.
        3. **Alerts**: Highlight any potential red flags (e.g. high spending relative to income if applicable, though looking at raw numbers).
        4. **Commendations**: Positive habits if any.
        
        Format the response in clean Markdown. Keep it friendly but professional.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            if "429" in str(e) or "Quota exceeded" in str(e):
                return "⏳ **Rate Limit Exceeded**: You are using the free tier of Gemini API which has strict limits. Please wait a minute and try again, or switch to a different model in the sidebar."
            return f"❌ Error generating insights: {str(e)}"
