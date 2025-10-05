from requests import Response
import json

def show_status(response: Response) -> None:
    print(f'[{response.status_code}] -> ', end='')
    try:
        print(json.dumps(response.json(), indent=4))
    except json.JSONDecodeError:
        print("No response body.")


def get_auth() -> dict:
    with open('../data/key.json', 'r') as file:
        key = json.load(file)
    return key
