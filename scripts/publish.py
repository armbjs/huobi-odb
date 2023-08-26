import os
import re
import tomlkit
import tomli_w


def main():
    print("os.getcwd()", os.getcwd())

    with open("pyproject.toml", mode="rt", encoding="utf-8") as fp:
        config = tomlkit.load(fp)
    print("config", config)

    current_version_str = config['tool']['poetry']['version']
    print("current_version_str", current_version_str)

    major_version, minor_version, patch_version = [int(x) for x in current_version_str.split(".")]
    new_patch_version = patch_version + 1
    new_version = f"{major_version}.{minor_version}.{new_patch_version}"

    print("new_version", new_version)

    config['tool']['poetry']['version'] = new_version
    with open("pyproject.toml", mode="wb") as fp:
        tomli_w.dump(config, fp)

    cmd_str = "poetry publish -r pdr --build"
    os.system(cmd_str)

    return

    with open("./docker/Dockerfile", "rt") as f:
        original_dockerfile = f.read()

        replaced_dockerfile = re.sub(pattern=r"==([0-9]+.[0-9]+.[0-9]+)",
                                     string=original_dockerfile,
                                     repl=f"=={new_version}")

    with open("./docker/Dockerfile", "wt") as f:
        f.write(replaced_dockerfile)

    project_name = config['tool']['poetry']['name']
    workflow_file_name = f"{project_name}-docker-image-publish.yaml"

    with open(f"../../.github/workflows/{workflow_file_name}", "rt") as f:
        original_file = f.read()

        replaced_file = re.sub(pattern=r":([0-9]+.[0-9]+.[0-9]+)",
                               string=original_file,
                               repl=f":{new_version}")

    with open(f"../../.github/workflows/{workflow_file_name}", "wt") as f:
        f.write(replaced_file)