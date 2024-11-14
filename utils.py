import requests
import re
import os
from mistralai import Mistral
import json
from prompts import *
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, List
from urllib.parse import quote_plus
import concurrent.futures
import random

class LLM:
    def __init__(self):
        pass
    
    
    def extract_query(self, text: str) -> str:
        pattern = r"```(.*?)```"
        matches = re.findall(pattern, text, re.DOTALL)
        data = matches[0] if matches else text
        data = data if "json" not in data.split("\n")[0].lower() else "\n".join(data.split("\n")[1:])
        return data


    def ask_Mistral(self, question, sys="You're a helpful assistant.", JSON= False, model = "mistral-large-2407"):
        try:
            self.Mistral_Client = Mistral(
                    api_key=random.choice(os.environ.get('MISTRAL_KEY').split()),
                )
            for i in range(10):
                try:
                    if JSON:
                        response = self.Mistral_Client.chat.complete(
                        model=model,
                        messages=[{"role":"system","content":sys},{"role":"user","content":question}],
                        temperature =  0.1,
                        top_p = 0.1,
                        response_format = {
                                "type": "json_object",
                            }
                    )
                        data = self.extract_query(response.choices[0].message.content)
                        print("data: ", data)
                        return json.loads(data)
                    else:
                        response = self.Mistral_Client.chat.complete(
                        model=model,
                        messages=[{"role":"system","content":sys},{"role":"user","content":question}],
                        temperature =  0.1,
                        top_p = 0.1
                    )
                        return response.choices[0].message.content
                    
                except Exception as e:
                    print(e)
                    print(response.choices[0].message.content)

        except Exception as e:
            print(e)

class server:
    def __init__(self):
        self.llm_client = LLM()
        self.search_client = Search_Tool()
   
    def start_questioning(self, data):
        chat_history, patient_details = data
        if len(chat_history)<16:
            prompt = str(patient_details) +  '\n' + str(chat_history) + '\n' + DIAGONOSING_PROMPT
        else:
            prompt = str(patient_details) +  '\n' + str(chat_history) + '\n' + DECIDING_PROMPT
        
        content = self.llm_client.ask_Mistral(sys = "You're DOCTOR AI.", question=prompt, JSON=True)

        if content['status'] == 'success':
            disease = content['disease']
            content = self.generate_conclusion(disease)
        else:
            content = content['questions']

        
        return {"id": chat_history[-1]['id']+1,
                "sender": "doctor",
                "content": content,
                "time": str(datetime.now().strftime("%I:%M %p")),
                "avatar": "static/trendy-doctor-concepts-vector.jpg"}
    
    def generate_conclusion(self, disease):
        urls = self.search_client.search(f"medication for {disease}", 5)

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            urls = [i['url'] for i in urls]
            results = executor.map(self.search_client.scrape_page, urls)
            results = list(results)

        # with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        #     prompts = [str(i) + WEBPAGE_EXTRACTOR.replace("[[[disease]]]", disease) for i in results]
        #     def ask_mistral(prompt):
        #         return self.llm_client.ask_Mistral(question=prompt, model="open-mistral-nemo", JSON=True)
        #     results = executor.map(ask_mistral, prompts)
        #     results = list(results)

        # report = self.llm_client.ask_Mistral(question=str(results) + INFORM_PATIENT_PROMPT)
        # return report

        return results


DEBUG = False  

def log_debug(message):
    if DEBUG:
        print(f"DEBUG: {message}")


class Search_Tool:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,/;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.google.com/',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

    def scrape_page(self, url: str, header_disabled = False, Get_Soup = False) -> Dict[str, Any]:
        try:
            if header_disabled:
                response = requests.get(url, timeout=5)
            else:
                response = requests.get(url, headers=self.headers, timeout=5)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            data = []
            for h2 in soup.find_all(['h2', 'h3', 'h4']):
                section = {}
                section['h'] = h2.text.strip()
                p = h2.find_next(['p', 'ul'])
                section['p'] = ''
                section['ul'] = ''
                while p and p.name in ['p', 'ul']:
                    if p.name == 'p':
                        section['p'] += p.text.strip() + ' '
                    elif p.name == 'ul':
                        for li in p.find_all('li'):
                            section['ul'] += li.text.strip() + ', '
                    p = p.find_next(['p', 'ul'])
                section['p'] = section['p'].strip()
                section['ul'] = section['ul'].strip(', ').strip()

                if "medi" in section['h'].lower() or "medi" in section['h'].lower() or "treat" in section['h'].lower() or "prescr" in section['h'].lower() or "antibi" in section['h'].lower() or "diagnos" in section['h'].lower():
                    data.append(section)

            if Get_Soup:
                return (response.text, data)
            return data
        except requests.RequestException as e:
            try:
                return self.scrape_page(url=url, header_disabled=True, timeout=5)
            except:
                print(f"Error scraping {url}: {str(e)}")
                return None
            return None






    def search(self, query: str, no_of_results: int) -> List[Dict[str, Any]]:
        log_debug(f"Performing web search for: {query}")
        search_results = self._perform_web_search(query, no_of_results)
        filtered_results = self._filter_search_results(search_results)
        deduplicated_results = self._remove_duplicates(filtered_results)
        log_debug(f"Found {len(deduplicated_results)} unique results")
        return deduplicated_results[:no_of_results]

    def _perform_web_search(self, query: str, no_of_results: int) -> List[Dict[str, Any]]:
        encoded_query = quote_plus(query)
        search_url = f"https://www.google.com/search?q={encoded_query}&num={no_of_results * 2}"
        log_debug(f"Search URL: {search_url}")
        
        try:
            log_debug("Sending GET request to Google")
            response = requests.get(search_url, headers=self.headers, timeout=5)
            log_debug(f"Response status code: {response.status_code}")
            response.raise_for_status()
            
            log_debug("Parsing HTML with BeautifulSoup")
            soup = BeautifulSoup(response.text, 'html.parser')
            
            log_debug("Searching for result divs")
            search_results = []
            for g in soup.find_all('div', class_='g'):
                log_debug("Processing a search result div")
                anchor = g.find('a')
                title = g.find('h3').text if g.find('h3') else 'No title'
                url = anchor.get('href', 'No URL') if anchor else 'No URL'
                
                description = ''
                description_div = g.find('div', class_=['VwiC3b', 'yXK7lf'])
                if description_div:
                    description = description_div.get_text(strip=True)
                else:
                    description = g.get_text(strip=True)
                
                log_debug(f"Found result: Title: {title[:30]}..., URL: {url[:30]}...")
                search_results.append({
                    'title': title,
                    'description': description,
                    'url': url
                })
            
            log_debug(f"Successfully retrieved {len(search_results)} search results for query: {query}")
            return search_results
        except requests.RequestException as e:
            log_debug(f"Error performing search: {str(e)}")
            return []

    def _filter_search_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        filtered = [result for result in results if result['description'] and result['title'] != 'No title' and result['url'].startswith('https://')]
        log_debug(f"Filtered to {len(filtered)} results")
        return filtered

    def _remove_duplicates(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        seen_urls = set()
        unique_results = []
        for result in results:
            if result['url'] not in seen_urls:
                seen_urls.add(result['url'])
                unique_results.append(result)
        log_debug(f"Removed duplicates, left with {len(unique_results)} results")
        return unique_results
