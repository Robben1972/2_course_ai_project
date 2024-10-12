import google.generativeai as genai
from environs import Env

env = Env()
env.read_env()

genai.configure(api_key=env("GEMINI_API_KEY"))


def text_generate(text):
    model = genai.GenerativeModel('gemini-1.5-pro')
    response = model.generate_content(text)
    return response.text


print(text_generate('Can you generate 10 python basic questions, with 3 answers'))
