import json
import os
from fireworks.client import Fireworks
from langchain_core.prompts import PromptTemplate
from prompts import search_prompt_system, relevant_prompt_system

# use ENV variables
MODEL = "accounts/fireworks/models/llama-v3p1-70b-instruct"
api_key_fireworks = os.getenv("FIREWORKS_API_KEY")

###TODO: MAKE SURE THIS IS CHANGED FOR LATER!!
TEMPERATURE = 0.0

client = Fireworks(api_key=api_key_fireworks)

def get_answer(query, contexts, date_context):
    system_prompt_search = PromptTemplate(input_variables=["date_today"], template=search_prompt_system)

    messages = [
        {"role": "system", "content": system_prompt_search.format(date_today=date_context)},
        {"role": "user", "content": "User Question : " + query + "\n\n CONTEXTS :\n\n" + contexts}
    ]

    try:
        stream = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            stream=True,
            temperature=TEMPERATURE,
        )

        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content

    except Exception as e:
        print(f"Error during get_answer_fireworks call: {e}")
        yield "data:" + json.dumps(
            {'type': 'error', 'data': "We are currently experiencing some issues. Please try again later."}) + "\n\n"

def get_relevant_questions(contexts, query):
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": relevant_prompt_system},
                {"role": "user", "content": "User Query: " + query + "\n\n" + "Contexts: " + "\n" + contexts + "\n"}
            ],
            response_format={"type": "json_object"},
            temperature=TEMPERATURE,
        )

        return response.choices[0].message.content
    except Exception as e:
        print(f"Error during RELEVANT FIREWORKS ***************: {e}")
        return {}
