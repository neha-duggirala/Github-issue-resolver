
import os
from dotenv import load_dotenv

load_dotenv()
OWNER = "neha-duggirala"
REPO = "Github-issue-resolver"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
PULL_NUMBER = 1