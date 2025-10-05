import zipfile, json, os, subprocess
import typer, requests, pyzipper
from dotenv import load_dotenv
from pathlib import Path
from utils import *

load_dotenv()

aegis = typer.Typer()

AEGIS_URL = 'http://localhost:8000'
ENC_KEY = os.getenv("ENC_KEY").encode()

@aegis.command()
def register(username: str, password: str):
    confirm_password = input("Confirm your password: ")

    if password != confirm_password:
        print("Password doesn't match.")
        return

    response = requests.post(f'{AEGIS_URL}/register', json={
        "username": username, "password": password
    })

    show_status(response)

    if response.status_code == 200:
        with open('../data/key.json', 'w') as jfile:
            jfile.write(json.dumps({
                "Authorization": f"Bearer {response.json().get("Token")}" 
            }, indent=4))


@aegis.command()
def login(username: str, password: str):
    confirm_password = input("Confirm your password: ")

    if password != confirm_password:
        print("Password doesn't match.")
        return

    response = requests.post(f'{AEGIS_URL}/login', json={
        "username": username, "password": password
    })

    show_status(response)

    if response.status_code == 200:
        with open('../data/key.json', 'w') as jfile:
            jfile.write(json.dumps({
                "Authorization": f"Bearer {response.json().get("Token")}" 
            }, indent=4))


@aegis.command()
def upload(filename: str):
    filepath = Path(filename)

    if filepath.is_dir():
        with zipfile.ZipFile(f'{filepath.name}.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(filepath):
                for file in files:
                    path = os.path.join(root, file)
                    arcname = os.path.relpath(path, filepath)
                    zipf.write(path, arcname=arcname)
                    
    elif filepath.is_file():
        with zipfile.ZipFile(f'{filepath.stem}.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(str(filepath), os.path.basename(filepath))

    with open(f'{filepath.stem}.zip', 'rb') as file:
        key = get_auth()

        files = {"files": (f'{filepath.stem}.zip', file, 'application/zip')}
        response = requests.post(f"{AEGIS_URL}/upload", files=files, headers=key)

    subprocess.run(f'del /s /q "{filepath.stem}.zip"', shell = True)

    show_status(response)


@aegis.command()
def list():
    with open('../data/key.json', 'r') as jsonfile:
        key = json.load(jsonfile)
    
    response = requests.get(f"{AEGIS_URL}/list", headers=key)

    show_status(response)


@aegis.command()
def download(filename: str):
    key = get_auth()

    response = requests.get(f'{AEGIS_URL}/download/{filename}', headers=key, stream=True)

    show_status(response)

    with open(f'{filename}.zip', 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)
    
    with pyzipper.AESZipFile(
            f'{filename}.zip', 'r', 
            compression=pyzipper.ZIP_DEFLATED, 
            encryption=pyzipper.WZ_AES) as file:
        file.extractall(path='../backups/',pwd=ENC_KEY)

    subprocess.run(f'del /s /q "{filename}.zip"', shell=True)


@aegis.command()
def delete(filename: str):
    with open('../data/key.json', 'r') as filejson:
        key = json.load(filejson)

    response = requests.delete(f'{AEGIS_URL}/delete/{filename}', headers=key)
    
    show_status(response)


if __name__ == '__main__':
    aegis()
