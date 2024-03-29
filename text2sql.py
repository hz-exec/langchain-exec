import json
import os
import sqlite3

from langchain.agents import AgentType, ZeroShotAgent, AgentExecutor
from langchain.agents.structured_chat.prompt import FORMAT_INSTRUCTIONS
from langchain.chains import LLMChain
from langchain.globals import set_debug
from langchain_community.agent_toolkits import SQLDatabaseToolkit, create_sql_agent
from langchain_community.agent_toolkits.sql.prompt import SQL_PREFIX
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_openai import OpenAI


def json2sql(json_text):
    db = sqlite3.connect(os.getenv('SQLITE_DB_PATH'))
    cursor = db.cursor()

    sql = """DROP TABLE IF EXISTS product;"""
    cursor.execute(sql)

    sql = """CREATE TABLE IF NOT EXISTS product (
    name TEXT NOT NULL,
    price_tag REAL NOT NULL,
    list_price REAL NOT NULL
    );"""
    cursor.execute(sql)

    data = json.loads(json_text)
    products = data['products']
    for product in products:
        def _to_float(s):
            if s is None:
                return "0.0"
            return float(s.replace('$', ''))

        name = product['name']['name']
        price_tag = _to_float(product['price_tag']['name'])
        list_price = _to_float(product['list_price']['name'])
        sql = f"""INSERT INTO product (name, price_tag, list_price) VALUES ("{name}", {price_tag}, {list_price});"""
        cursor.execute(sql)
        db.commit()

    sql = """SELECT * FROM product;"""
    cursor.execute(sql)
    results = cursor.fetchall()
    for row in results:
        print(row)

    db.close()


def text2sql(text):
    llm = OpenAI()
    db = SQLDatabase.from_uri("sqlite:///" + os.getenv('SQLITE_DB_PATH'))
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)

    # debug tools
    tools = toolkit.get_tools()
    for tool in tools:
        print(tool)

    executor = create_sql_agent(
        llm=llm,
        toolkit=toolkit,
        # verbose=True,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    )
    result = executor.invoke(text)
    print("=" * 100)
    print(result)

    # llm = OpenAI(temperature=0, model="gpt-3.5-turbo-0613")
    # executor = create_sql_agent(
    #     llm=llm,
    #     toolkit=toolkit,
    #     # verbose=True,
    #     agent_type=AgentType.OPENAI_FUNCTIONS,
    # )
    # result = executor.run(text)
    # print(result)


# def text2sql2(text):
#     llm = OpenAI()
#     db = SQLDatabase.from_uri("sqlite:///" + os.getenv('SQLITE_DB_PATH'))
#     toolkit = SQLDatabaseToolkit(db=db, llm=llm)
#     tools = toolkit.get_tools()
#
#     prefix = SQL_PREFIX.format(dialect=toolkit.dialect, top_k=10)
#     prompt = ZeroShotAgent.create_prompt(
#         prefix=prefix,
#         tools=tools,
#         format_instructions=FORMAT_INSTRUCTIONS,
#         input_variables=None,
#     )
#     print("Prompt: ", prompt, "\n")
#
#     llm_chain = LLMChain(llm=llm, prompt=prompt)
#     agent = ZeroShotAgent(llm_chain=llm_chain, prompt=prompt, tools=tools)
#     agent_executor = AgentExecutor.from_agent_and_tools(agent=agent, tools=tools)
#     result = agent_executor.run(text)
#     print(result)


def prepare_db():
    with open(os.getenv('JSON_DATA_PATH'), 'r') as f:
        json_text = f.read()
    json2sql(json_text)


def main():
    prepare_db()

    # enable debug
    set_debug(True)
    while True:
        text = input('Enter a text: (q to quit)')
        if text == 'q':
            break
        if text == '':
            text = 'What is the lowest price of the product?'
        text2sql(text)
        # text2sql2(text)


if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()

    main()
