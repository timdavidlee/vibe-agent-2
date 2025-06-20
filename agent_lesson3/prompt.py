from langchain_core.prompts import PromptTemplate

parse_prompt = PromptTemplate.from_template("""
Extract the following fields from the user message below. 
If a field is not specified, leave it null. Output in JSON format only.

For the dates, please convert any date-like instructions into a date in YYYY-MM-DD format.
If no year or month is specified, use the the year 2024 and the current system month. Ignore any time-of-day instructions.

Expected output Fields:
- country: The destination country
- start_date: Start date in YYYY-MM-DD format
- end_date: End date in YYYY-MM-DD format
- rate: Maximum daily rate, in decimal format, should be a currency-like value
- limit: Maximum number of results (default to 10)

Message: {input}
""")
