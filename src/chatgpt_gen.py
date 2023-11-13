import requests
import csv

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
