import json
import os
import sqlite3

from langchain.agents import AgentType
from langchain_community.agent_toolkits import SQLDatabaseToolkit, create_sql_agent
from langchain_community.llms.openai import OpenAI
from langchain_community.utilities.sql_database import SQLDatabase


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
    executor = create_sql_agent(
        llm=llm,
        toolkit=toolkit,
        verbose=True,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    )
    result = executor.run(text)
    print(result)


def main():
    with open(os.getenv('JSON_DATA_PATH'), 'r') as f:
        json_text = f.read()
    json2sql(json_text)
    while True:
        text = input('Enter a text: (q to quit)')
        if text == 'q':
            break
        text2sql(text)


if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()

    main()
