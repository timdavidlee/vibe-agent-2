import json
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph
from typing import TypedDict, Annotated
import typer
import requests
from loguru import logger


from agent_lesson2.prompt import parse_prompt
from webservice.schemas import TripSearchRequest, TripSearchResultsResponse


cli_app = typer.Typer()


llm = ChatOpenAI(model="gpt-4")

parser = JsonOutputParser(pydantic_object=TripSearchRequest)
chain = parse_prompt | llm | parser


def parse_trip_query_node(state):
    user_message = state["user_input"]
    trip_query = chain.invoke({"input": user_message})
    logger.info(f"Parsed Query: {trip_query}")
    return {"parsed_query": TripSearchRequest.model_validate(trip_query)}


def call_search_api_node(state):
    """Call REST API to perform actual search"""
    trip_query: TripSearchRequest = state["parsed_query"]
    logger.info(f"Sending Query to API: {trip_query}")

    # Example API call - replace with your actual endpoint
    api_url = "http://localhost:9009/api/trip/openings/search"

    try:
        response = requests.get(api_url, params=trip_query.model_dump(), timeout=10)
        response.raise_for_status()
        search_results: TripSearchResultsResponse = response.json()
        logger.info(f"Search Results: {search_results}")
        return {
            "search_results": TripSearchResultsResponse.model_validate(search_results),
            "api_status": "success",
            "parsed_query": trip_query,
        }
    except requests.RequestException as e:
        logger.error(f"Error calling API: {str(e)}")
        return {
            "search_results": None,
            "api_status": f"error: {str(e)}",
            "parsed_query": trip_query,
        }


class ChatState(TypedDict):
    user_input: str
    parsed_query: TripSearchRequest
    search_results: TripSearchResultsResponse
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
    logger.warning("User Input: {}".format(user_input))
    result = langgraph_app.invoke({"user_input": user_input})
    logger.info(
        "Parsed Query: {}".format(result["parsed_query"].model_dump_json(indent=2))
    )
    if result["search_results"]:
        logger.info("Search Results Below:")
        for row in result["search_results"].results:
            logger.info(row.model_dump_json(indent=2))


if __name__ == "__main__":
    cli_app()
