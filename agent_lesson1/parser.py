from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph
from typing import TypedDict, Annotated
import typer

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


class ChatState(TypedDict):
    user_input: str
    parsed_query: TripQuery


graph = StateGraph(ChatState)
graph.add_node("parse_query", parse_trip_query_node)
graph.set_entry_point("parse_query")
graph.set_finish_point("parse_query")

langgraph_app = graph.compile()


@cli_app.command()
def parse_query(user_input: Annotated[str, typer.Option("--user-input", "-s", help="The user input to parse")]):
    """Parse a user query into a TripQuery object"""

    result = langgraph_app.invoke({"user_input": user_input})
    print(result["parsed_query"])


if __name__ == "__main__":
    cli_app()