import os
import sys
import typing as t
import subprocess as s
from enum import IntEnum
import logging
import argparse

logging.basicConfig(
    format="{asctime} - {levelname} - {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO
)

class SupportedHost(IntEnum):
    GITHUB = 1

REPO_HOST = {
    "github" : SupportedHost.GITHUB
}

def is_missing(args_dict: t.Dict[str, t.Any]) -> bool:
    for elem in args_dict:
        if args_dict[elem] is None:
            return True
    return False
    

class RepoHost:
    def fetch(self: t.Self, user_name: str, repo_name: str, **kwargs: t.Dict[str, t.Any]) -> bool:
        raise NotImplemented("Not yet implemented!")


class GithubHost(RepoHost):
    _url = "https://github.com"
    _target_user = None
    _target_repo = None
    _is_remote = False
    _force = False
    
    def __init__(self: t.Self, target_manifest_repo=None, target_manifest_user=None, remote=False, force=False):
        self._target_repo = target_manifest_repo
        self._target_user = target_manifest_user
        self._force = force

    def fetch(self: t.Self, user_name: str, repo_name: str, **kwargs: t.Dict[str, t.Any]) -> bool:
        repo_url = f"{self._url}/{user_name}/{repo_name}"
        package_id = repo_name.lower()
        package_path = f"packages/{package_id[0]}/{package_id}"
        result = (
            "[package]\n"
            f"name={repo_name}\n"
            f"url={repo_url}\n"
        )
        file_exists = os.path.isfile(f"{package_path}/{package_id}.ini")
        if file_exists and not self._force:
            logging.error("Manifest file already exists!")
            return False
        else:
            ret = s.run(["git", "ls-remote", repo_url, "--quiet"])
            if ret.returncode != 0:
                logging.error(f"Could not fetch repository `{repo_url}`, verify the spelling of the repository name or check if internet connection is stable")
                return False
            try:
                os.makedirs(package_path, exist_ok=True)
                with open(f"{package_path}/{package_id}.ini", "w") as f:
                    f.write(result)
                    f.close()
                    return True  
            except:
                logging.error(f"An error occurred while creating Manifest file `{package_path}/{package_id}.ini`")
                return False
            

def main(argv: t.List[str]) -> None:
    parser = argparse.ArgumentParser(
        prog="python tools/yank.py",
        description="Yank your favorite repository",
        usage=("%(prog)s [options]")
        
    )
    parser.add_argument("-s", help="Host of the source repository, in lowercase e.g. github")
    parser.add_argument("-u", help="Source repository user name")
    parser.add_argument("-r", help="Source repository name")
    parser.add_argument("--manifest", nargs = "?", help="Remote manifest repository")
    parser.add_argument("--force", action="store_true", help="Force manifest file regeneration")
    
    if len(argv) < 2:
        parser.print_help()
    else:
        args = parser.parse_args(args=argv[1:])
        args_dict = {"-s": args.s, "-r": args.r, "-u": args.u}
        force = args.force
        if is_missing(args_dict):
            missing_opt = " ".join([x for x in args_dict if args_dict[x] is None])
            logging.error(f"Missing option {missing_opt}")
            parser.print_help()
            return
        match (REPO_HOST[args_dict["-s"]]):
            case SupportedHost.GITHUB:
                if not GithubHost(force=force).fetch(args_dict["-u"], args_dict["-r"]):
                    logging.error("Yanking failed!")
                else:
                    logging.info("Yanking successfull!")
                        


if __name__ == "__main__":
    main(sys.argv)