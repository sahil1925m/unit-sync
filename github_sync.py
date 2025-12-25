import os
import base64
import requests
from pathlib import Path
import streamlit as st

class GithubSync:
    def __init__(self, token, repo_name, branch='main'):
        """
        token: GitHub Personal Access Token
        repo_name: 'username/repository'
        """
        self.token = token
        self.repo = repo_name
        self.branch = branch
        self.base_url = f"https://api.github.com/repos/{repo_name}"
        self.headers = {"Authorization": f"token {token}"}

    def push_file(self, file_path, commit_message):
        """Push a single file to GitHub"""
        file_path = Path(file_path)
        try:
            with open(file_path, "rb") as f:
                content = base64.b64encode(f.read()).decode()

            # Get relative path from root (assumed to be app root)
            # If absolute, make relative to CWD
            try:
                rel_path = file_path.relative_to(os.getcwd())
            except ValueError:
                rel_path = file_path.name # Fallback

            # Check if file exists to get SHA (for update)
            url = f"{self.base_url}/contents/{rel_path}"
            get_resp = requests.get(url, headers=self.headers)
            
            payload = {
                "message": commit_message,
                "content": content,
                "branch": self.branch
            }

            if get_resp.status_code == 200:
                payload["sha"] = get_resp.json()["sha"]
            
            resp = requests.put(url, json=payload, headers=self.headers)
            if resp.status_code in [200, 201]:
                return True, "Synced to Cloud"
            else:
                return False, f"Sync Error: {resp.json().get('message')}"
        except Exception as e:
            return False, str(e)

    def pull_file(self, file_path):
        """Pull a single file from GitHub"""
        # ... logic for pulling if needed ...
        # For this app, we mainly worry about Pushing new notes.
        # Full sync is complex.
        pass
