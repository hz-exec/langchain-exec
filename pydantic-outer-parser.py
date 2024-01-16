from typing import List

from langchain.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import OpenAI
from pydantic import BaseModel, Field, validator, field_validator


class CodeRisk(BaseModel):
    description: str = Field(description="A brief description of the security risk")
    severity: str = Field(description="The level of severity of the risk")
    recommendations: List[str] = Field(description="Recommended actions to mitigate the risk")

    @field_validator("severity")
    @classmethod
    def severity_must_be_valid(cls, field: str):
        if field not in ["Low", "Medium", "High", "Critical"]:
            raise ValueError("Invalid severity level!")
        return field


def main():
    temperature = 0.0
    model = OpenAI(temperature=temperature)

    code_snippet_query = """
Analyze the following block of code for potential security risks:
public void authenticate(String username, String password) {
    if (username.equals("admin") && password.equals("password123")) {
        
    }
}
"""

    parser = PydanticOutputParser(pydantic_object=CodeRisk)
    format_instructions = parser.get_format_instructions()
    prompt = PromptTemplate(
        template="Identify any potential security risks in the code snippet provided.\n"
                 "{format_instructions}\n"
                 "{query}\n",
        input_variables=["query"],
        partial_variables={"format_instructions": format_instructions},
    )
    _input = prompt.format_prompt(query=code_snippet_query)
    output = model.invoke(_input.to_string())
    parsed_output = parser.parse(output)
    print(parsed_output)


if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()

    main()

