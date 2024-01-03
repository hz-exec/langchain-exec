# pip install langchain
# pip install openai
# pip install python-dotenv
# pip install langchain-google-genai

def openai_chain():
    from langchain_community.chat_models import ChatOpenAI
    llm = ChatOpenAI(model_name="gpt-3.5-turbo-1106", max_tokens=100)
    # response = llm.invoke("What LLM is?")
    # print(response)

    from langchain_google_genai import ChatGoogleGenerativeAI
    llm = ChatGoogleGenerativeAI(model="gemini-pro")
    response = llm.invoke("What LLM is?")
    print(response)

    from langchain.prompts import ChatPromptTemplate
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Your are an LLM expert."),
        ("user", "{input}"),
    ])

    # chain = prompt | llm
    # response = chain.invoke({"input": "What LLM is?"})
    # print(response)

    from langchain_core.output_parsers import StrOutputParser
    output_parser = StrOutputParser()

    chain = prompt | llm | output_parser
    response = chain.invoke({"input": "What LLM is?"})
    print(response)


def local_chain():
    pass


def main():
    from dotenv import load_dotenv
    load_dotenv()

    openai_chain()


if __name__ == '__main__':
    main()
