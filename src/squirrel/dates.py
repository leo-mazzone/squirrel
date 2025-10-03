import json
from datetime import datetime
from typing import Any, Dict

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable

from squirrel.prompts import CleaningStrOutputParser, llm_engine
from squirrel.utils import clean_markdown_code_blocks


def get_current_date_context() -> str:
    """
    Get current date context information for the LLM.

    Returns:
        String with current date information for the LLM to use
    """
    now = datetime.now()
    return f"""
Current date context (use this for resolving relative dates):
- Today's date: {now.strftime("%Y-%m-%d (%A)")}
- Current year: {now.year}
- Current month: {now.strftime("%B %Y")}
- Current week: Week {now.strftime("%U")} of {now.year}
- Current quarter: Q{(now.month - 1) // 3 + 1} {now.year}
"""


def date_processing_chain() -> Runnable:
    """
    Create an LLM chain that processes natural language date expressions.

    Returns:
        Runnable chain that takes a question and returns processed dates
    """
    system_prompt = """
    You are a date processing assistant. Your job is to identify relative date
    expressions 
    in user questions and convert them to specific date ranges suitable for SQL queries.

    Given a user question and current date context, you should:
    1. Identify any relative date expressions (like "this year", "last month",
       "Q1 2024", "three months ago", etc.)
    2. Convert them to specific date ranges using SQL-compatible format
    3. Replace the relative expressions in the question with clear, specific
       date references
    4. Return the results in valid JSON format

    Return your response as a JSON object with these fields:
    - "processed_question": The question with relative dates replaced by
      specific date references
    - "date_expressions_found": Array of relative date expressions that were identified
    - "sql_date_filters": Array of SQL-compatible date filter expressions

    For SQL date filters, use formats like:
    - "BETWEEN '2024-01-01' AND '2024-12-31'" for date ranges
    - ">= '2024-01-01'" for "since" or "after" dates  
    - "<= '2024-12-31'" for "before" or "until" dates

    Be flexible and handle various ways people express dates:
    - "this year" → current year range
    - "last year" → previous year range  
    - "Q1 2024" → January 1 to March 31, 2024
    - "three months ago" → calculate from current date
    - "beginning of last year" → January 1 of previous year
    - "summer 2023" → approximate summer months of 2023
    - "early 2024" → first few months of 2024

    If no relative dates are found, return the original question unchanged.

    IMPORTANT: Return only valid JSON, no additional text or formatting.
    """

    human_prompt = """
    {current_date_context}

    User question: {question}

    Please process any relative date expressions in this question and return
    the result as JSON.
    """

    prompt = ChatPromptTemplate.from_messages(
        [("system", system_prompt), ("human", human_prompt)]
    )

    return prompt | llm_engine | CleaningStrOutputParser()


def process_question_dates(question: str) -> Dict[str, Any]:
    """
    Process a user question to resolve relative date expressions.

    Args:
        question: The user's original question

    Returns:
        Dictionary with processed question and date information
    """
    chain = date_processing_chain()

    try:
        result_str = chain.invoke(
            {"question": question, "current_date_context": get_current_date_context()}
        )

        # Clean any markdown code blocks from the response
        cleaned_result = clean_markdown_code_blocks(result_str)

        # Parse the JSON response
        result = json.loads(cleaned_result)

        return {
            "processed_question": result.get("processed_question", question),
            "date_expressions_found": result.get("date_expressions_found", []),
            "sql_date_filters": result.get("sql_date_filters", []),
            "original_question": question,
        }

    except (json.JSONDecodeError, Exception) as e:
        # Graceful fallback if date processing fails
        print(f"Date processing failed: {e}")
        return {
            "processed_question": question,
            "date_expressions_found": [],
            "sql_date_filters": [],
            "original_question": question,
        }


def enhance_sql_prompt_with_dates(sql_filters: list[str]) -> str:
    """
    Generate additional context for SQL generation based on identified date filters.

    Args:
        sql_filters: List of SQL date filter expressions

    Returns:
        Additional context string for SQL generation
    """
    if not sql_filters:
        return ""

    return f"""
Additional date filter context:
The following date filters have been identified and should be incorporated into your SQL
query:
{chr(10).join(f"- {filter_expr}" for filter_expr in sql_filters)}

Use these filters in your WHERE clause as appropriate for the database schema.
"""
