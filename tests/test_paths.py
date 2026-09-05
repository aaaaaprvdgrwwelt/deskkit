from pathlib import Path

from deskkit.paths import subfolder_of


def test_subfolder_of_returns_direct_child_of_root():
    result = subfolder_of(Path("/series/Show/Season 1/ep.mkv"), Path("/series"))
    assert result == Path("/series/Show")


def test_subfolder_of_returns_root_when_path_lies_directly_in_root():
    result = subfolder_of(Path("/movies/movie.mkv"), Path("/movies"))
    assert result == Path("/movies")


def test_subfolder_of_returns_root_when_path_is_not_under_root():
    result = subfolder_of(Path("/other/file.mkv"), Path("/movies"))
    assert result == Path("/movies")
