from deskkit.matching import normalize_title, title_similarity


def test_normalize_title_strips_case_punctuation_and_articles():
    assert normalize_title("The Matrix: Reloaded!") == "matrix reloaded"
    assert normalize_title("Der Herr der Ringe") == "herr ringe"


def test_normalize_title_empty_input():
    assert normalize_title("") == ""
    assert normalize_title(None) == ""


def test_normalize_title_collapses_whitespace():
    assert normalize_title("Star   Wars\n\tEpisode") == "star wars episode"


def test_title_similarity_identical_after_normalization():
    assert title_similarity("The Matrix", "matrix") == 1.0


def test_title_similarity_empty_side_is_zero():
    assert title_similarity("", "Matrix") == 0.0
    assert title_similarity("Matrix", "") == 0.0


def test_title_similarity_partial_match_between_zero_and_one():
    score = title_similarity("Futurama", "Futuramaa")
    assert 0.0 < score < 1.0


def test_title_similarity_unrelated_titles_low_score():
    score = title_similarity("Futurama", "The Great British Bake Off")
    assert score < 0.3
