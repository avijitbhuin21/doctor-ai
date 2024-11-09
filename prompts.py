GREET_PROMPT = '''This is the details of a patient. You are reuested to generate a greetings message that asks him/her if they have any premedical conditions that we should look out for while diagonosing her current symptoms. Keep it extremely brief.'''

DIAGONOSING_PROMPT = '''Based on this data, you have to find out the disease of the patient.
                        If your confidence is not more than 80% then ask more questions to the patient for further clerence and get a better understanding of the symptoms.
                        Try to guess the disease, ask questions only if it's necessary.
                        Use this JSON schema when generating answer:
                        {"status": status (str), "questions": questions (str), "disease": disease (str)}
                        
                        NOTE: if you choose to question, set the status as "pending" and disease as "un-identified".
                              if you have identified the disease, set the status as "success" and questions as "[]".
                              
                              You may ask only 1 question at a time and upto 5 questions.
                              You must put the JSON answer between two ```.
                              
                        Answer:
                        '''

DECIDING_PROMPT = '''Based on this chat and Patient details you have to guess the disease of the patient.
                     Use this JSON schema when generating answer:
                        {"status": status (str), "disease": disease (str)}

                     You must put the JSON answer between two ```.
                        '''