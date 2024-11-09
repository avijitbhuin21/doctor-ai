import requests
import re
import os
import urllib.parse
import openai
import json
import random
from prompts import *
from datetime import datetime

class LLM:
    def __init__(self):
        pass
    
    
    def extract_query(self, text: str) -> str:
        pattern = r"```(.*?)```"
        matches = re.findall(pattern, text, re.DOTALL)
        return matches[0] if matches else text


    def ask_SambaNova(self, sys, question, JSON= False, model = "Meta-Llama-3.1-405B-Instruct"):
        try:
            self.SambaNova_Client = openai.OpenAI(
                    api_key=random.choice(os.environ.get("SAMBANOVA_KEYS").split()),
                    base_url="https://api.sambanova.ai/v1",
                )
            for i in range(10):
                try:
                    response = self.SambaNova_Client.chat.completions.create(
                        model=model,
                        messages=[{"role":"system","content":sys},{"role":"user","content":question}],
                        temperature =  0.1,
                        top_p = 0.1
                    )
                    print(response.choices[0].message.content)
                    if JSON:
                        data = self.extract_query(response.choices[0].message.content)
                        print("data: ", data)
                        return json.loads(data)
                    else:
                        return response.choices[0].message.content
                except Exception as e:
                    print(e)

        except Exception as e:
            print(e)

class server:
    def __init__(self):
        self.llm_client = LLM()
   
    def start_questioning(self, data):
        chat_history, patient_details = data
        if len(chat_history)<16:
            prompt = str(patient_details) +  '\n' + str(chat_history) + '\n' + DIAGONOSING_PROMPT
        else:
            prompt = str(patient_details) +  '\n' + str(chat_history) + '\n' + DECIDING_PROMPT
        
        content = self.llm_client.ask_SambaNova(sys = "You're DOCTOR AI.", question=prompt, JSON=True)

        content = content['disease'] if content['status'] == 'success' else content['questions']

        
        return {"id": chat_history[-1]['id']+1,
                "sender": "doctor",
                "content": content,
                "time": str(datetime.now().strftime("%I:%M %p")),
                "avatar": "static/trendy-doctor-concepts-vector.jpg"}