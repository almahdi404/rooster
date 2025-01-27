from pathlib import Path
from typing import Generator

import pygit2 as git
from packaging.version import Version

from rooster._config import Config

TAG_PREFIX = "refs/tags/"


def get_tags(config: Config, target: Path) -> list[str]:
    repo = git.repository.Repository(target.absolute())

    references = repo.listall_references()
    return [
        _parse_tag_reference(config, ref)
        for ref in references
        if ref.startswith(TAG_PREFIX + config.version_tag_prefix)
    ]


def _parse_tag_reference(config: Config, reference: str) -> str:
    return reference[len(TAG_PREFIX + config.version_tag_prefix) :]


def get_commits_between(
    config: Config,
    target: Path,
    first_version: Version | None = None,
    second_version: Version | None = None,
) -> Generator[git.Commit, None, None]:
    """
    Yield all commits between two tags
    """
    repo = git.repository.Repository(target.absolute())
    first_commit = (
        repo.lookup_reference(
            TAG_PREFIX + config.version_tag_prefix + str(first_version)
        )
        .peel()
        .id
        if first_version is not None
        else None
    )
    second_commit = (
        repo.lookup_reference(
            TAG_PREFIX + config.version_tag_prefix + str(second_version)
        )
        .peel()
        .id
        if second_version is not None
        # TODO: Lookup main branch
        else repo.revparse_single("main").id
    )
    # Walk backwards from the second commit until we find the first commit
    for commit in repo.walk(second_commit):
        if commit.id == first_commit:
            break
        yield commit


def get_remote_url(target: Path, remote_name: str = "origin") -> str | None:
    repo = git.repository.Repository(target.absolute())
    names = {remote.name for remote in repo.remotes}
    if remote_name not in names:
        return None
    return repo.remotes[remote_name].url
