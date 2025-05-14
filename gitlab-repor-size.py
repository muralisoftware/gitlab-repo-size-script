import requests

# Replace with your GitLab personal access token and GitLab URL
GITLAB_TOKEN = 'YOUR_TOKEN'
GITLAB_URL = 'https://gitlab.com'  # Change if you're using a self-hosted GitLab

headers = { 'Private-Token': GITLAB_TOKEN }

def bytes_to_human_readable(num_bytes):
    """
    Converts bytes to the nearest higher unit (KB, MB, GB, TB, etc.)
    """
    units = ["Bytes", "KB", "MB", "GB", "TB", "PB"]
    size = float(num_bytes)
    for unit in units:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} PB"

def get_branch_size(project_id, branch):
    archive_url = f"{GITLAB_URL}/api/v4/projects/{project_id}/repository/archive.tar.gz?sha={branch}"
    response = requests.get(archive_url, headers=headers, stream=True)

    if response.status_code == 200:
        size_bytes = 0
        for chunk in response.iter_content(chunk_size=8192):
            size_bytes += len(chunk)
        size_mb = size_bytes / 1024 / 1024
        return round(size_mb, 2)
    else:
        print(f"Failed to get archive for branch {branch} of project {project_id}")
        return None
    
def list_projects():
    page = 1
    per_page = 100  # max 100
    all_projects = []

    while True:
        response = requests.get(
            f'{GITLAB_URL}/api/v4/projects?membership=true&per_page={per_page}&page={page}',
            headers=headers
        )
        if response.status_code != 200:
            print("Failed to fetch projects:", response.status_code, response.text)
            break

        projects = response.json()
        if not projects:
            break

        all_projects.extend(projects)
        page += 1

    for project in all_projects:
        project_id = project['id']
        name = project['name']
        web_url = project['web_url']
        path_with_namespace = project['path_with_namespace']

        """ # Get project stats individually
        branches_url = f"{GITLAB_URL}/api/v4/projects/{project_id}/repository/branches"
        branches_response = requests.get(branches_url, headers=headers)

        if branches_response.status_code != 200:
            print(f"Failed to fetch branches for {name}")
            continue

        branches = branches_response.json()
        total_project_size = 0

        print(f"\n📁 {name} ({web_url})")

        for branch in branches:
            branch_name = branch['name']
            size = get_branch_size(project_id, branch_name)
            total_project_size += size
            if size is not None:
                print(f"  - 🌿 Branch `{branch_name}`: ~{size} MB")

        print(f"🧮 Total Compressed Size (All Branches): ~{round(total_project_size, 2)} MB") """

        projectRequest = requests.get(f"{GITLAB_URL}/api/v4/projects/{project['id']}?statistics=true", headers=headers)

        if projectRequest.status_code != 200:
            print(f"Failed to fetch the project {name}")
            continue

        project = projectRequest.json()

        print(f'\n📁 {name} ({path_with_namespace})')

        print('🧮 Total project size:', bytes_to_human_readable(project['statistics']['repository_size']))

if __name__ == '__main__':
    list_projects()
