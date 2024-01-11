from langchain import hub
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.tools.retriever import create_retriever_tool
from langchain_community.chat_models import ChatOpenAI
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.tools.tavily_search import TavilySearchResults, TavilyAnswer
from langchain_community.vectorstores.docarray import DocArrayInMemorySearch
from langchain_openai import OpenAIEmbeddings


def example():
    # search tool
    search_tool = TavilyAnswer()
    # result = search_tool.run("What is the capital of France?")
    # print(result)

    # retriever tool
    loader = WebBaseLoader("https://docs.smith.langchain.com/overview")
    docs = loader.load()
    print("docs are: ", docs)
    documents = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200).split_documents(docs)
    vector = DocArrayInMemorySearch.from_documents(documents, OpenAIEmbeddings())
    retriever = vector.as_retriever()
    # result = retriever.get_relevant_documents("How to upload a dataset")
    # print("result is: ", result)

    retriever_tool = create_retriever_tool(
        retriever,
        "langsmith_search",
        "Search for information about LangSmith. For any questions about LangSmith, you must use this tool!"
    )
    # result = retriever_tool.run("What is LangSmith?")
    # print(result)

    tools = [search_tool, retriever_tool]

    # create the agent
    llm = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0)
    prompt = hub.pull("hwchase17/openai-functions-agent")
    print("prompt is: ", prompt)

    agent = create_openai_functions_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    # # run the agent
    # result = executor.invoke({"input": "What is LangSmith?"})
    # print(result)

    search_result = search_tool.invoke("weather in San Francisco")
    print("search result is: ", search_result)

    result = executor.invoke({"input": "whats the weather in sf?"})
    print("result is: ", result)


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    example()
