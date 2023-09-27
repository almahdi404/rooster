from pathlib import Path
from typing import Generator

import pygit2 as git
from packaging.version import Version

VERSION_REF_PREFIX = "refs/tags/v"


def get_tags(target: Path) -> list[str]:
    repo = git.repository.Repository(target.absolute())

    references = repo.listall_references()
    return [
        _parse_tag_reference(ref)
        for ref in references
        if ref.startswith(VERSION_REF_PREFIX)
    ]


def _parse_tag_reference(reference: str) -> str:
    return reference[len(VERSION_REF_PREFIX) :]


def get_commits_between(
    target: Path,
    first_version: Version | None = None,
    second_version: Version | None = None,
) -> Generator[git.Commit, None, None]:
    """
    Yield all commits between two tags
    """
    repo = git.repository.Repository(target.absolute())
    first_commit = (
        repo.lookup_reference(VERSION_REF_PREFIX + str(first_version)).peel().id
        if first_version is not None
        else None
    )
    second_commit = (
        repo.lookup_reference(VERSION_REF_PREFIX + str(second_version)).peel().id
        if second_version is not None
        # TODO: Lookup main branch
        else repo.revparse_single("main").id
    )
    # Walk backwards from the second commit until we find the first commit
    for commit in repo.walk(second_commit):
        if commit.id == first_commit:
            break
        yield commit


def get_remote_url(target: Path, remote_name: str = "origin") -> str:
    repo = git.repository.Repository(target.absolute())
    return repo.remotes[remote_name].url
