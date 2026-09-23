import requests

API = "https://api.example.com"


def fetch_data(path):
    response = requests.get(f"{API}/{path}", timeout=10)
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    print(fetch_data("items"))
