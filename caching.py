import hashlib
import logging
import os
import requests

cache = {}

"""Calculate hash of url in cache"""
def hash(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()

"""GET url or read from cache/ if it exists"""
def get(url: str, **kwargs) -> bytes:
    cache_path = f"cache/{hash(url)}"
    if os.path.exists(cache_path):
        with open(cache_path, "rb") as f:
            return f.read()
    logging.info(f"Downloading: {url}")
    response = requests.get(url, **kwargs)
    if response.status_code == 200:
        if not os.path.isdir("cache"):
            os.mkdir("cache")
        with open(cache_path, "wb") as f:
            f.write(response.content)
        return response.content
    raise Exception(f"HTTP ERROR {response.status_code}: {response.text}")

"""Remove url from cache so that it will be downloaded again"""
def remove_from_cache(url: str):
    os.remove(f"cache/{hash(url)}")
