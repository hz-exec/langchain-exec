from langchain import hub


def prompt_viewer():
    prompt1 = hub.pull("hwchase17/openai-functions-agent")
    print("prompt1 is: \n", prompt1)

    prompt2 = hub.pull("hwchase17/react")
    print("prompt2 is: \n", prompt2)


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    prompt_viewer()
