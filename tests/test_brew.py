from brew_migrator.core.brew import (
    exact_match,
    normalize_app_name,
    parse_installed_cask_apps,
    rank_matches,
)


def test_normalize_app_name():
    assert normalize_app_name("Visual Studio Code") == "visual-studio-code"
    assert normalize_app_name("1Password") == "1password"
    assert normalize_app_name("  Google  Chrome ") == "google-chrome"
    assert normalize_app_name("Raycast™") == "raycast"


def test_rank_matches_puts_exact_token_first():
    tokens = ["gzoom", "zoom-for-it-admins", "zoom", "photozoom-pro"]
    assert rank_matches("Zoom", tokens) == ["zoom", "zoom-for-it-admins", "gzoom", "photozoom-pro"]


def test_rank_matches_ignores_separators():
    tokens = ["visual-studio-code@insiders", "visual-studio-code", "code"]
    assert rank_matches("Visual Studio Code", tokens) == [
        "visual-studio-code",
        "visual-studio-code@insiders",
    ]


def test_rank_matches_empty_query():
    assert rank_matches("   ", ["zoom"]) == []


def test_exact_match():
    assert exact_match("Zoom", ["zoom-for-it-admins", "zoom"]) == "zoom"
    assert exact_match("Zoom", ["zoom-for-it-admins"]) is None


def test_parse_installed_cask_apps():
    casks = [
        {"token": "1password", "artifacts": [{"app": ["1Password.app"]}, {"zap": []}]},
        {"token": "renamed", "artifacts": [{"app": ["Orig.app", {"target": "Renamed.app"}]}]},
        {"token": "cli-only", "artifacts": [{"binary": ["tool"]}, ["not", "a", "dict"]]},
    ]
    assert parse_installed_cask_apps(casks) == {
        "1Password": "1password",
        "Orig": "renamed",
        "Renamed": "renamed",
    }
