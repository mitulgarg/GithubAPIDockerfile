import requests
import pandas as pd

# Replace with your GitHub Personal Access Token
GITHUB_TOKEN = "YOUR-PAT-TOKEN"

def search_repos_with_dockerfile(query="Dockerfile in:path", num_results=10, page=1):
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    url = f"https://api.github.com/search/repositories?q={query}&per_page={num_results}&page={page}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()["items"]
    else:
        print("Error in repository search:", response.json())
        return []

def get_repo_contents(owner, repo, path=""):
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching contents for {owner}/{repo} at path '{path}':", response.json())
        return None

def extract_structure(owner, repo, path=""):
    folder_structure = []
    dockerfile_content = None
    
    def recursive_structure(path):
        nonlocal dockerfile_content
        contents = get_repo_contents(owner, repo, path)
        if contents:
            for item in contents:
                if item["type"] == "file":
                    if item["name"] == "Dockerfile":
                        dockerfile_content = requests.get(item["download_url"]).text
                    folder_structure.append(f"File: {item['path']}")
                elif item["type"] == "dir":
                    folder_structure.append(f"Directory: {item['path']}")
                    recursive_structure(item["path"])
    
    recursive_structure(path)
    return dockerfile_content, folder_structure

def main():
    # Specify the search parameters
    query = "Dockerfile in:path"
    num_results = 1  # Adjust for the number of repos you want to fetch
    page = 1

    # Search for repositories containing Dockerfiles
    repositories = search_repos_with_dockerfile(query, num_results, page)

    # Initialize data structure for the dataset
    data = {
        "Repository Name": [],
        "Repository URL": [],
        "Dockerfile Content": [],
        "Folder Structure": []
    }

    # Process each repository to extract Dockerfile and folder structure
    for repo in repositories:
        owner = repo["owner"]["login"]
        repo_name = repo["name"]
        print(f"Processing repository: {owner}/{repo_name}")
        
        # Extract Dockerfile content and folder structure
        dockerfile_content, folder_structure = extract_structure(owner, repo_name)

        # Append the data to our dataset
        data["Repository Name"].append(repo_name)
        data["Repository URL"].append(repo["html_url"])
        data["Dockerfile Content"].append(dockerfile_content)
        data["Folder Structure"].append(folder_structure)

    # Create a DataFrame and save it as a CSV file
    df = pd.DataFrame(data)
    df.to_csv("github_dockerfiles_dataset.csv", index=False)
    print("Dataset saved to github_dockerfiles_dataset.csv")

if __name__ == "__main__":
    main()
