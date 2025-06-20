from langchain_core.prompts import PromptTemplate

parse_prompt = PromptTemplate.from_template("""
Extract the following fields from the user message below. 
If a field is not specified, leave it null. Output in JSON format only.

Fields:
- country: The destination country
- start_date: Start date in YYYY-MM-DD format
- end_date: End date in YYYY-MM-DD format
- rate: Maximum daily rate, in decimal format, should be a currency-like value
- limit: Maximum number of results (default to 10)

Message: {input}
""")
