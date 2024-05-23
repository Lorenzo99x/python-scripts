import argparse
from pathlib import Path
import gitlab
import git
import shutil


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-l", "--list", type=str, help="Files of repositories", required=True
    )
    parser.add_argument(
        "-s", "--source", type=str, help="GitLab Private token source.", required=True
    )
    parser.add_argument(
        "-d", "--destination", type=str, help="GitLab Private token destination.", required=True
    )
    parser.add_argument(
        "urlsource", help="Gitlab URL source. (https://gitlab.url.source)"
    )
    parser.add_argument(
        "urldestination", help="Gitlab URL source. (https://gitlab.url.destination)"
    )

    args = parser.parse_args()
    return args


def clone_repository(repo_name : str, clone_path : Path, gl) -> git.Repo:
    project = gl.projects.get(repo_name)

    clone_url = project.http_url_to_repo

    repo = git.Repo.clone_from(clone_url, clone_path)

    print(f'Repository {repo_name} cloned to {clone_path}')

    return repo


def set_new_origin(repo: git.Repo, new_origin_url: str):
    origin = repo.remotes.origin
    origin.set_url(new_origin_url)
    print(f'New origin URL set to {new_origin_url}')
    print(origin.url)
    return origin


def push_changes(origin, branch):
    origin.push(refspec=f'{branch}:{branch}')
    print(f'Changes pushed to {new_origin_url}')


def remove_clone(clone_path: Path):
    parent = clone_path.parent
    shutil.rmtree(clone_path)
    print(f'Directory {clone_path} removed')
    while parent != parent.root:
        try:
            parent.rmdir()
        except OSError:
            break
        parent = parent.parent


def get_main_branch(repo: git.Repo):
    if 'main' in repo.heads:
        return repo.heads['main']
    elif 'master' in repo.heads:
        return repo.heads['master']
    else:
        return repo.active_branch


if __name__ == "__main__":

    args = parse_args()

    url_source = args.urlsource
    url_dest = args.urldestination

    gl = gitlab.Gitlab(url_source, private_token=args.source, ssl_verify=False)

    with open(args.list, 'r') as read_file:
        for line in read_file:
            if not (line):
                continue
            line = line.strip()
            clone_path = Path(line)
            new_origin_url = url_dest.replace('https://', f'https://oauth2:{args.destination}@') + '/' + line
            repo = clone_repository(line, clone_path, gl)
            origin = set_new_origin(repo, new_origin_url)
            branch = get_main_branch(repo)
            push_changes(origin, branch)
            remove_clone(clone_path)
