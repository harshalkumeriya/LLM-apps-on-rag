import requests
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from requests import Response
from typing import List, Dict

class WebScraper:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def _get_full_answer(self, txt: str) -> str:
        # Define the start and end phrases
        start_phrase = "MUTUAL FUND CALCULATORS"
        end_phrase = "ready to invest"
        start = txt.find(start_phrase) + len(start_phrase)
        end = txt.find(end_phrase)
        return txt[start:end].strip()

    def get_data(self, website_url: str) -> Response:
        # Send a request to the FAQ page
        response = requests.get(website_url)
        response.raise_for_status()  # Check if the request was successful
        return response

    def scrape_data(self, response: Response) -> List[Dict[str, str]]:
        scraped_data = []
        soup = BeautifulSoup(response.text, 'html.parser')
        sections = soup.find_all("div", {"class": "accordionbucket"})

        for section in sections:
            section_name = section.find("div", {"class": "bucket-title"}).get_text(strip=True)
            articles = section.find_all('article', {"role": "article"})
            for article in articles:
                scraped_data.append(self._extract_article_data(article, section_name))

        return scraped_data

    def _extract_article_data(self, article, section_name: str) -> Dict[str, str]:
        question_element = article.find("h2", {"class": "bucket-article-title"})
        if not question_element:
            return {}

        q_text = question_element.get_text(strip=True)
        answer_element = article.find("p")
        if not answer_element:
            return {}

        answer_link = self._get_answer_link(answer_element)
        full_answer = self._fetch_full_answer(answer_link)

        return {
            "section": section_name,
            "question": q_text,
            "answer": full_answer,
            "link": self.base_url + answer_link if answer_link else ""
        }

    def _get_answer_link(self, answer_element) -> str:
        read_more = answer_element.find("a")
        return read_more.get("href") if read_more else ""

    def _fetch_full_answer(self, answer_link: str) -> str:
        if not answer_link:
            return ""
        
        answer_url = urljoin(self.base_url, answer_link)
        try:
            response = requests.get(answer_url)
            response.raise_for_status()
            page_text = response.text
            return self._get_full_answer(page_text)
        except Exception as e:
            print(f"Failed to fetch full answer from {answer_url}: {e}")
            return ""

    @staticmethod
    def save(data: List[Dict[str, str]], filename: str = 'data.json') -> None:
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4)
        print(f"Data has been written to {filename}")

if __name__ == "__main__":
    base_url = 'https://www.mutualfundssahihai.com'
    website_url = f"{base_url}/en/your-questions"
    
    scraper = WebScraper(base_url)
    response = scraper.get_data(website_url)
    data = scraper.scrape_data(response)
    scraper.save(data, filename="mutual_fund_faq.json")