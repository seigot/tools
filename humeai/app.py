from dotenv import load_dotenv
import os
from hume import AsyncHumeClient
import asyncio
from contextlib import contextmanager
from typing import Generator, Protocol

load_dotenv()
api_key = os.getenv("HUME_API_KEY")
if not api_key:
    raise EnvironmentError("HUME_API_KEY not found in environment variables")

hume = AsyncHumeClient(api_key=api_key)
print(hume)