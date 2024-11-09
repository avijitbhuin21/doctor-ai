from llm import LLM
import json
from search import Disease_details

search_client = Disease_details()


class Template:
    def __init__(self):
        self.llm_client = LLM()

    def Determine_disease(self, question):
        p = json.loads(question[0]['content'])
        q = question[2]['content']
        user_data = "\n".join([f"{i['role']}: {i['content']}" for i in question[3:]])
        prompt = f'''    
            Profile of the patient:
            Name: {p['name']}
            Sex: {p['sex']}
            Age: {p['age']}
            Height: {p['height']}
            Weight: {p['weight']}
            pre-existing medical conditions: {q}

            And Medical Issue: 
            {p['medicalIssue']}
                                    '''
        data = self.llm_client.ask_SambaNova(sys = """
                                                    1. Begin with a <thinking> section. Everything in this section is invisible to the user.
                                                    2. Inside the thinking section:
                                                        a. Briefly analyze the question or task you’ve been given.
                                                        b. Present a clear plan of steps to solve the problem.
                                                        c. Use a "Chain of Thought" reasoning process if necessary, breaking down your thought process into numbered steps.
                                                        d. Consider any potential challenges or issues that may arise.

                                                    3. Include a <reflection> section for each idea where you:
                                                        a. Review your reasoning to ensure accuracy.
                                                        b. Check for potential errors or oversights.
                                                        c. Adjust your conclusion if necessary.

                                                    4. Be sure to close all reflection sections.
                                                    5. Close the thinking section with </thinking>.
                                                    6. You must provide your final answer in an <output> </output> section.

                                             """,
                question = """You will be provided with a statement or some symptoms entered by a patient.
                            Please generate a JSON response based on the following schemas:
                            Note:You may ask up to 8 questions to help identify the disease or health condition.  
                                Ask as less questions as possible.      
                                Do not include any explanations or apologies in your responses.
                                Do not include any text except the generated answer.
                            {
                            "status": "success",
                            "data":{
                            "type": str("disease"/"Health_Condition"),
                            "name": str
                                    }
                            }
                             OR
                            {
                            "status": "failed",
                            "questions": list(str) 
                            }\n"""+prompt+"\n"+user_data)
        if data['status'] == 'success':
            disease = data['data']['name']
            data = search_client.get_meds(disease, patient_profile=prompt)
        return data
    
    def greet(self, details):
        data = self.llm_client.ask_groq(sys = '''  
                                    You are Doctor AI. You are helpful, smart, kind, and loving.
                                    You will be provided with details of a patient. You have to greet the patient clamly and kindly without using any expressions such as **warm smile** or **kindly**.
                                    You must ask the patient if they have any medical condition such as high or low blood pressure or sugar or maybe some kind of heart disease, anything that needs to be taken into consideration while checking for the disease.
                                    Also keep the greetings as consice as possible. 
                                    Construct the answer in JSON format following this schema:{"message": message}
                                    '''
                             ,question= details)
        return data
    
    def Analyze_answers(self, sys, question):
        data = self.llm_client.ask_SambaNova(sys=sys, question=question)


