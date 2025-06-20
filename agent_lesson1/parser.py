from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph
from typing import TypedDict, Annotated
import typer
import requests

from agent_lesson1.schemas import TripQuery
from agent_lesson1.prompt import parse_prompt


cli_app = typer.Typer()


llm = ChatOpenAI(model="gpt-4")

parser = JsonOutputParser(pydantic_object=TripQuery)
chain = parse_prompt | llm | parser


def parse_trip_query_node(state):
    user_message = state["user_input"]
    trip_query = chain.invoke({"input": user_message})
    return {"parsed_query": trip_query}


def call_search_api_node(state):
    """Call REST API to perform actual search"""
    trip_query = state["parsed_query"]

    # Example API call - replace with your actual endpoint
    api_url = "https://api.example.com/search"

    try:
        response = requests.post(
            api_url,
            json={
                "country": trip_query.country,
                "start_date": trip_query.start_date,
                "end_date": trip_query.end_date,
                "rate": trip_query.rate,
                "limit": trip_query.limit,
            },
            timeout=10,
        )
        response.raise_for_status()
        search_results = response.json()
        return {"search_results": search_results, "api_status": "success"}
    except requests.RequestException as e:
        return {"search_results": None, "api_status": f"error: {str(e)}"}


class ChatState(TypedDict):
    user_input: str
    parsed_query: TripQuery
    search_results: dict
    api_status: str


graph = StateGraph(ChatState)
graph.add_node("parse_query", parse_trip_query_node)
graph.add_node("call_api", call_search_api_node)
graph.set_entry_point("parse_query")
graph.add_edge("parse_query", "call_api")
graph.set_finish_point("call_api")

langgraph_app = graph.compile()


@cli_app.command()
def parse_query(
    user_input: Annotated[
        str, typer.Option("--user-input", "-s", help="The user input to parse")
    ],
):
    """Parse a user query into a TripQuery object and call search API"""

    result = langgraph_app.invoke({"user_input": user_input})
    print("Parsed Query:", result["parsed_query"])
    print("API Status:", result["api_status"])
    if result["search_results"]:
        print("Search Results:", result["search_results"])


if __name__ == "__main__":
    cli_app()
