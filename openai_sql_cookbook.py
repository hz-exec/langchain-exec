import json
import os
import sqlite3
import openai
import requests
from termcolor import colored
from text2sql import prepare_db
from tenacity import retry, wait_random_exponential, stop_after_attempt


GPT_MODEL = "gpt-3.5-turbo-0613"


def get_table_names(conn):
    """Return a list of table names."""
    table_names = []
    tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
    for table in tables.fetchall():
        table_names.append(table[0])
    return table_names


def get_column_names(conn, table_name):
    """Return a list of column names."""
    column_names = []
    columns = conn.execute(f"PRAGMA table_info('{table_name}');").fetchall()
    for col in columns:
        column_names.append(col[1])
    return column_names


def get_database_info(conn):
    """Return a list of dicts containing the table name and columns for each table in the database."""
    table_dicts = []
    for table_name in get_table_names(conn):
        columns_names = get_column_names(conn, table_name)
        table_dicts.append({"table_name": table_name, "column_names": columns_names})
    return table_dicts


def ask_database(conn, query):
    """Function to query SQLite database with a provided SQL query."""
    try:
        results = str(conn.execute(query).fetchall())
    except Exception as e:
        results = f"query failed with error: {e}"
    return results


def execute_function_call(conn, message):
    if message["tool_calls"][0]["function"]["name"] == "ask_database":
        query = json.loads(message["tool_calls"][0]["function"]["arguments"])["query"]
        results = ask_database(conn, query)
    else:
        results = f"Error: function {message['tool_calls'][0]['function']['name']} does not exist"
    return results


def pretty_print_conversation(messages):
    role_to_color = {
        "system": "red",
        "user": "green",
        "assistant": "blue",
        "tool": "magenta",
    }

    for message in messages:
        if message["role"] == "system":
            print(colored(f"system: {message['content']}\n", role_to_color[message["role"]]))
        elif message["role"] == "user":
            print(colored(f"user: {message['content']}\n", role_to_color[message["role"]]))
        elif message["role"] == "assistant" and message.get("function_call"):
            print(colored(f"assistant: {message['function_call']}\n", role_to_color[message["role"]]))
        elif message["role"] == "assistant" and not message.get("function_call"):
            print(colored(f"assistant: {message['content']}\n", role_to_color[message["role"]]))
        elif message["role"] == "tool":
            print(colored(f"function ({message['name']}): {message['content']}\n", role_to_color[message["role"]]))


@retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(3))
def chat_completion_request(messages, tools=None, tool_choice=None, model=GPT_MODEL):
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + os.getenv("OPENAI_API_KEY")
    }
    json_data = {"model": model, "messages": messages}
    if tools is not None:
        json_data.update({"tools": tools})
    if tool_choice is not None:
        json_data.update({"tool_choice": tool_choice})
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=json_data,
        )
        return response
    except Exception as e:
        print("Unable to generate ChatCompletion response")
        print(f"Exception: {e}")
        return e


def main():
    conn = sqlite3.connect(os.getenv('SQLITE_DB_PATH'))
    database_schema_dict = get_database_info(conn)
    database_schema_string = "\n".join(
        [
            f"Table: {table['table_name']}\nColumns: {', '.join(table['column_names'])}"
            for table in database_schema_dict
        ]
    )
    print(database_schema_string)

    tools = [
        {
            "type": "function",
            "function": {
                "name": "ask_database",
                "description":
                    "Use this function to answer user questions about music. Input should be a fully formed SQL query.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": f"""
                                    SQL query extracting info to answer the user's question.
                                    SQL should be written using this database schema:
                                    {database_schema_string}
                                    The query should be returned in plain text, not in JSON.
                                    """,
                        }
                    },
                    "required": ["query"],
                },
            }
        }
    ]

    messages = [
        {
            "role": "system",
            "content": "Answer user questions by generating SQL queries against the Database."
         },
        {
            "role": "user",
            "content": "Hi, which is the most expensive product?"
        }
    ]

    chat_response = chat_completion_request(messages, tools)
    assistant_message = chat_response.json()["choices"][0]["message"]
    assistant_message['content'] = str(assistant_message["tool_calls"][0]["function"])
    messages.append(assistant_message)
    if assistant_message.get("tool_calls"):
        results = execute_function_call(conn, assistant_message)
        messages.append({
            "role": "tool",
            "tool_call_id": assistant_message["tool_calls"][0]['id'],
            "name": assistant_message["tool_calls"][0]["function"]["name"],
            "content": results})
    pretty_print_conversation(messages)


if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()
    prepare_db()

    main()
