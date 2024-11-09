import requests
from bs4 import BeautifulSoup
import warnings
import re
from llm import LLM
from duckduckgo_search import DDGS
llm_client = LLM()

warnings.filterwarnings("ignore")


class Disease_details:
    
    def __init__(self):
        pass
    

    def extract_query(self, text: str) -> str:
      pattern = r"```(.*?)```"
      matches = re.findall(pattern, text, re.DOTALL)
      return matches[0] if matches else text


    def extract_from_tags(self, text):
        pattern = r"<output>(.*?)</output>"
        matches = re.findall(pattern, text, re.DOTALL)
        data = matches[0] if matches else text
        return data.strip("\n").strip()


    def Search_on_the_Internet(self, query):
        print("Searching on the Internet...")
        results = DDGS().text(query, max_results=5)
        return [i['href'] for i in results]


    def get_meds(self, disease, patient_profile):
        links = self.Search_on_the_Internet(f"Buy Medicines for {disease} By Sanofi India Ltd")
        data = []
        for link in links:
            data.append(str([f"purchase link: {link}", self.extract_data(link)]))

        res = llm_client.ask_gemini_pro(sys="""
                                  You will be provided with some data by the user. You need to generate a Prescription from that.
                                  Gnerate the prescription based on the Patient Statement Provided.
                                  Include Links to Medicines. and a description of the patient situation.
                                  Also You Must Prioritise the Medicines Manufactured by Sanofi India Ltd.
                                  Generate it in JSON format. Use the following template when generating your response strictly.
                                  template:{
                                            "status": success
                                            "prescription": str(In Markdown Format)
                                            }
                                  Note: Do not include any explanations or apologies in your responses.
                                        Do not include any text except the generated answer.
                                        Return only the text in json format provided.
                                """,
                            question= patient_profile + "\nIdentified Disease: "+ disease + "\nMedications: " + "\n".join(data))

        return res


    def summerize(self, text):
        res = llm_client.ask_gemini_flash(sys="""
                                  You will be provided with some text by the user. You need to summerize the content.
                                  Use the answer in json format. Use the following template when generating your response strictly.
                                  template:{
                                            "meds": [{"name":str, "manufacturer":str}]
                                            }
                                  Note: Do not include any explanations or apologies in your responses.
                                        Do not include any text except the generated answer.
                                        Return only the text in json format provided.
                                """,
                            question="Text Content: " + text)
        print(res)        
        return res


    def extract_data(self, url):
        try:
            res = requests.get(url)
            soup = BeautifulSoup(res.content, 'html.parser')
            all_text = soup.get_text(separator='\n', strip=True)
            print(f"Extracted data from: {url}")
            return self.summerize(all_text)
        except:
            pass













    # def analyze_disease(self, convo):
    #     reflection_prompt = """You are Doctor-AI, designed to provide detailed, step-by-step responses. Your outputs should follow this structure:
    #                         1. Begin with a <thinking> section. Everything in this section is invisible to the user.
    #                         2. Inside the thinking section:
    #                           a. Briefly analyze the question or task you’ve been given.
    #                           b. Present a clear plan of steps to solve the problem.
    #                           c. Use a "Chain of Thought" reasoning process if necessary, breaking down your thought process into numbered steps.
    #                           d. Consider any potential challenges or issues that may arise.

    #                         3. Include a <reflection> section for each idea where you:
    #                           a. Review your reasoning to ensure accuracy.
    #                           b. Check for potential errors or oversights.
    #                           c. Adjust your conclusion if necessary.

    #                         4. Be sure to close all reflection sections.
    #                         5. Close the thinking section with </thinking>.
    #                         6. Provide your final answer in an <output> </output> section.

    #                         7. Always answer in the following JSON format within the <output> </output> section: 
    #                         {
    #                           "status":"success",
    #                           "disease": "disease_name",
    #                         }
    #                         8. If youre unable to decide, set the "status" as "failed" in json response.and the "disease" to None.
    #                         """
    #     base_prompt = """
    #               The Patient is having some symptoms.
    #               A Probable list of Diseases are provided Below, your job is to question the user until you get the right disease.
    #               Only one question should be asked at a time, in the given json format: ```{"status":"pending","question": "question1","disease":"None"}```
    #               Only when you are absolutely confident about the identification of the disease ans in this format: ```{"status":"success","disease":"disease1"}```
                  
    #               Note: Do not include any explanations or apologies in your responses.
    #                     Do not include any text except the generated answer.
    #                     Return only the text in json format provided.
    #                     Max Number of Questions allowed is 5. If exceeded and you cannot decide the disease, ask the patient to see a doctor.
    #                     Do not Repeat the Same Type of Question.
    #               """
    #     if self.history == []:
    #         self.history = [str(convo)]
    #     else:
    #         self.history = self.history + [str([f"Question no {len(self.history)}: "+str(convo)])]  
    #     question_prompt = "Patient's Statement:\n"+self.statement+"\n"+"Probable Disease list:\n"+str(self.diseases)+"\nChat History:\n"+"\n".join(self.history)

    #     for i in self.history:
    #         print(i)


    #     if 6-len(self.history) > 0:
    #         print(question_prompt)
    #         data = llm_client.ask_genai(sys=base_prompt,question=question_prompt)
    #     else:
    #         print("ANALYZING...")
    #         data = llm_client.ask_pro(sys=reflection_prompt,question=question_prompt, json_format = False)
    #     print(data)
    #     data = json.loads(self.extract_query(self.extract_from_tags(data)))
    #     if data['status'] != 'pending':
    #         self.history = []
    #     return data

