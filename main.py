import os
import logging
from dotenv import load_dotenv
from src.config import setup_logging
from src.data_loader import load_data
from src.chain_runner import analyze_dataframe

def main():
    load_dotenv()
    setup_logging()
    logger = logging.getLogger(__name__)

    if not os.getenv("GROQ_API_KEY"):
        raise EnvironmentError("GROQ_API_KEY not found in environment variables.")

    logger.info("Starting automated data analysis...")

    df = load_data("data/International_Education_Costs.csv")
    logger.info(f"Loaded dataframe with {len(df)} rows and {len(df.columns)} columns")

    # Example question
    question = "name of the cities of japan in the file?"

    try:
        code_snippet, result = analyze_dataframe(df, question)
        print("--- Generated Python Snippet ---")
        print(code_snippet)
        print("--- Result ---")
        print(result)
    except Exception as e:
        logger.exception("An error occurred during analysis.")
        print("Error:", e)

if __name__ == "__main__":
    main()
