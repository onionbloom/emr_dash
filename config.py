from os import getenv

from dotenv import load_dotenv

load_dotenv()
host = getenv("FTPHOST")
port = getenv("FTPPORT")
user = getenv("FTPUSER")
pwd = getenv("FTPPWD")
