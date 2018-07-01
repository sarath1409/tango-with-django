import requests, json
# import urllib.parse
def run_query(search_terms=None):

    search_url = "https://api.cognitive.microsoft.com/bing/v7.0/search"

    try:
        with open('./rango/bing_api.key', 'r') as f:
            bing_api_key = f.readline() 
    except:
        raise IOError('Read file error')

    

    headers = {"Ocp-Apim-Subscription-Key" : bing_api_key}
    params  = {"q": search_terms, "textDecorations":True, "textFormat": "HTML"}
    response = requests.get(search_url, headers=headers, params=params)
    response.raise_for_status()
    search_results = response.json()

    return search_results

def main():
    print("Parsing search")

if __name__ == "__main__":
    main()