import requests
from requests import Response
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def _get_full_answer(txt: str) -> str:
    # Define the start and end phrases
    start_phrase = "MUTUAL FUND CALCULATORS"
    end_phrase = "ready to invest"

    start = txt.find(start_phrase) + len(start_phrase)
    end = txt.find(end_phrase)
    output = txt[start:end]
    # print(output)
    return output

def get_data(website_url: str) -> Response:
    # Send a request to the FAQ page
    response = requests.get(website_url)
    response.raise_for_status()  # Check if the request was successful
    return response

def scrape_data(response: Response) -> list[dict]:
    scraped_data = []
    # Parse the FAQ page with the Strainer
    soup = BeautifulSoup(response.text, 'html.parser')
    sections = soup.find_all("div", {"class":"accordionbucket"})
    for section in sections:
        articles_title = section.find("div", {"class": "bucket-title"})
        section_name = articles_title.get_text()
        # print("\narticles_title: ", section_name) 
        articles = section.find_all('article', {"role":"article"})
        for article in articles:
            question = article.find("h2", {"class": "bucket-article-title"})
            if question:
                q_text = question.get_text(strip=True)
                # print("\nquestion: ", q_text)
            answer = article.find("p")
            if answer:
                # a_text = answer.get_text(strip=True)
                # print("\nshort_answer: ", a_text)
                read_more = answer.find("a")
                if read_more:
                    answer_link = read_more.get("href")
                    # print("\nread_more_link: ", answer_link)
                    answer_url = urljoin(base_url, answer_link)  # Resolve relative URL
                    # Fetch the detailed answer page
                    try:
                        answer_response = requests.get(answer_url)
                        answer_response.raise_for_status()  # Check if the request was successful
                        # Parse the detailed answer page with the Strainer
                        answer_soup = BeautifulSoup(answer_response.text, 'html.parser')
                        page_text = answer_soup.get_text( strip=True)
                        full_ans = _get_full_answer(str(page_text))
                    except:
                        full_ans = ""
                        continue
                    # print("\nfull_answer: ", full_ans[100:200])
                    # print("="*100)
                    scraped_data.append(
                        {
                            "section": section_name,
                            "question": q_text,
                            "answer": full_ans[56:-6],
                            "link": base_url+answer_link
                        }
                    )
    return scraped_data

def save(data, filename = 'data.json') -> None:
    import json
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)
    print(f"Data has been written to {filename}")

if __name__ == "__main__":
    # Base URL of the website
    base_url = 'https://www.mutualfundssahihai.com'
    website_url = "https://www.mutualfundssahihai.com/en/your-questions"
    response = get_data(website_url)
    data = scrape_data(response)
    save(data, filename="mutual_fund_faq.json")