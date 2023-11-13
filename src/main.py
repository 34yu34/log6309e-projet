import requests
import csv
import os
import shutil
import git
from radon.visitors import ClassVisitor

def search_github_repositories(api_url, query_params):
    response = requests.get(api_url, params=query_params)

    if response.status_code == 200:
        return response.json()['items']
    else:
        print(f"Error: {response.status_code}")
        return []

def write_to_csv(repositories, csv_filename):
    with open(csv_filename, mode='w', newline='', encoding='utf-8') as csv_file:
        fieldnames = ['Name', 'Description', 'URL', 'Stars', 'Forks', 'Lines of Code']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        writer.writeheader()
        for repo in repositories:
            writer.writerow({
                'Name': repo['name'],
                'Description': repo['description'],
                'URL': repo['html_url'],
                'Stars': repo['stargazers_count'],
                'Forks': repo['forks_count'],
                'Lines of Code': repo['size']
            })

def read_csv(csv_filename):
    data = []

    try:
        with open(csv_filename, mode='r', encoding='utf-8') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                data.append(row)
    except FileNotFoundError:
        print(f"Error: File '{csv_filename}' not found.")
    except Exception as e:
        print(f"Error reading CSV file: {e}")

    return data

#    for repo in repositories:
        # print(f"\nName: {repo['name']}")
        # print(f"Description: {repo['description']}")
        # print(f"URL: {repo['html_url']}")
        # print(f"Stars: {repo['stargazers_count']}")
        # print(f"Forks: {repo['forks_count']}")
        # print(f"Lines of Code: {repo['size']}")

def clone_and_analyze_repositories(repositories, keyword):
    result = []

    for repo in repositories:
        repo_name = repo['Name']
        repo_url = repo['URL']
        repo_path = f"repos/{repo_name}"

        try:
            # Clone the repository
            git.Repo.clone_from(repo_url, repo_path)

            # Analyze the code using radon
            total_classes_with_keyword = 0

            for root, dirs, files in os.walk(repo_path):
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            classes = ClassVisitor.from_code(content)
                            classes_with_keyword = [cls for cls in classes if keyword.lower() in cls.name.lower()]
                            total_classes_with_keyword += len(classes_with_keyword)

            result.append({'Name': repo_name, 'ClassesWithKeyword': total_classes_with_keyword})

        except Exception as e:
            print(f"Error analyzing repository '{repo_name}': {e}")
        finally:
            # Clean up: Remove the cloned repository
            if os.path.exists(repo_path):
                shutil.rmtree(repo_path)

    return result


def main():
    api_url = 'https://api.github.com/search/repositories'
    keyword = 'devops'
    min_lines_of_code = 10000  # You can adjust this threshold as needed
    csv_filename = 'repositories.csv'

    query_params = {
        'q': f'{keyword} size:>{min_lines_of_code}',
        'sort': 'stars',
        'order': 'desc'
    }

    repositories = search_github_repositories(api_url, query_params)

    print(f"Found {len(repositories)} repositories with more than {min_lines_of_code} lines of code and containing the keyword '{keyword}':")

    for repo in repositories:
        print(f"\nName: {repo['name']}")
        print(f"Description: {repo['description']}")
        print(f"URL: {repo['html_url']}")
        print(f"Stars: {repo['stargazers_count']}")
        print(f"Forks: {repo['forks_count']}")
        print(f"Lines of Code: {repo['size']}")

    write_to_csv(repositories, csv_filename)
    print(f"\nRepository information has been written to '{csv_filename}'.")

if __name__ == "__main__":
    main()
