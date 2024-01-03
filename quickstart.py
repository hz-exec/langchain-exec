# pip install langchain
# pip install openai
# pip install python-dotenv
# pip install langchain-google-genai

def langchain_llm():
    llms = []
    question = "What LLM is?"

    from langchain_community.chat_models import ChatOpenAI
    llmOpenAI = ChatOpenAI(model_name="gpt-3.5-turbo-1106", max_tokens=100)
    llms.append(llmOpenAI)
    response = llmOpenAI.invoke(question)
    print("gpt-3.5-turbo-1106:")
    print(response)

    from langchain_google_genai import ChatGoogleGenerativeAI
    llmGoogle = ChatGoogleGenerativeAI(model="gemini-pro", convert_system_message_to_human=True)
    llms.append(llmGoogle)
    response = llmGoogle.invoke(question)
    print("gemini-pro:")
    print(response)

    from langchain_community.llms import Ollama
    llmOllama = Ollama(model="llama2")
    llms.append(llmOllama)
    response = llmOllama.invoke(question)
    print("llama2:")
    print(response)

    for llm in llms:
        # response = llm.invoke("What LLM is?")
        # print(response)
        print("=" * 80)

        from langchain.prompts import ChatPromptTemplate
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Your are a Large Language Model (LLM) expert."),
            ("user", "{input}"),
        ])

        from langchain_core.output_parsers import StrOutputParser
        output_parser = StrOutputParser()

        chain = prompt | llm | output_parser
        response = chain.invoke({"input": question})
        print(response)


def main():
    from dotenv import load_dotenv
    load_dotenv()

    langchain_llm()


if __name__ == '__main__':
    main()
