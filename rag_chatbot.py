import pandas as pd
import google.generativeai as genai
import os


def get_ai_response(query: str, df: pd.DataFrame) -> str:
    """
    Generates an AI response to a query based on the provided DataFrame.
    """
    # Configure the generative AI model
    # Ensure you have your Google API key set as an environment variable
    # For example: os.environ["GOOGLE_API_KEY"] = "YOUR_API_KEY"
    try:
        genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    except KeyError:
        return "Google API Key not found. Please set the GOOGLE_API_KEY environment variable."

    model = genai.GenerativeModel("models/gemini-2.5-flash")

    # Reduce DataFrame size for the LLM
    # 1. Select relevant columns
    relevant_cols = [
        "Date",
        "Plant",
        "Material",
        "Unrestricted_Stock",
        "Stock_Sell_Value",
        "Loss_Value",
    ]
    df_reduced = df[relevant_cols].copy()

    # 2. Sort by Date and take a limited number of rows (e.g., last 200 entries)
    df_reduced["Date"] = pd.to_datetime(df_reduced["Date"])
    df_reduced = df_reduced.sort_values(by="Date", ascending=False).head(5000)

    # Convert reduced DataFrame to a string format for the LLM
    inventory_data_str = df_reduced.to_markdown(index=False)

    # Construct the prompt for the LLM
    prompt = f"""
    You are an AI assistant specialized in inventory management.
    You will be provided with inventory data in a table format and a user's question.
    Your task is to answer the user's question based *only* on the provided inventory data.
    If the answer cannot be found in the provided data, please state that you cannot find the information.

    Inventory Data:
    {inventory_data_str}

    User Question: {query}

    AI Response:
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"An error occurred while generating the AI response: {e}"
