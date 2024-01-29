import requests
from datetime import datetime, timedelta
import base64

def get_contributor_details(url, pat):
    # Calculate dates for the last 90 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)

    # Set up authentication
    headers = {'Authorization': 'Basic ' + base64.b64encode(f':{pat}'.encode()).decode()}

    # Fetch all repositories in the organization
    repos_url = f"{url}/_apis/git/repositories?api-version=5.0"
    repos_response = requests.get(repos_url, headers=headers)
    if repos_response.status_code != 200:
        raise Exception(f"Failed to retrieve repositories: {repos_response.status_code}")

    repositories = repos_response.json()['value']

    # Dictionary to hold contributor details
    contributors = {}

    # Iterate through repositories and get commits
    for repo in repositories:
        repo_id = repo['id']
        repo_name = repo['name']
        commits_url = f"{url}/_apis/git/repositories/{repo_id}/commits?searchCriteria.fromDate={start_date.strftime('%Y-%m-%d')}&searchCriteria.toDate={end_date.strftime('%Y-%m-%d')}&api-version=5.0"
        commits_response = requests.get(commits_url, headers=headers)

        if commits_response.status_code != 200:
            continue  # Skip to next repository if there's an error

        commits = commits_response.json()['value']
        for commit in commits:
            author_email = commit['author']['email']
            author_name = commit['author']['name']
            if author_email not in contributors:
                contributors[author_email] = {'name': author_name, 'repos': set()}
            contributors[author_email]['repos'].add(repo_name)

    return contributors

# TFS Server URL and PAT
tfs_url = 'http://your-tfs-server:8080/tfs/DefaultCollection'
pat = 'YOUR_PERSONAL_ACCESS_TOKEN'

# Retrieve contributor details
contributor_details = get_contributor_details(tfs_url, pat)

# Print details
print(f"Total unique contributors in the last 90 days: {len(contributor_details)}")
for email, details in contributor_details.items():
    repos = ', '.join(details['repos'])
    print(f"Contributor: {details['name']} ({email}), Repositories: {repos}")