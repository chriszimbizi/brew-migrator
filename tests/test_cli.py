from brew_migrator.cli import scan_applications


def test_scan_applications_prefers_earlier_folders(tmp_path):
    system = tmp_path / "Applications"
    user = tmp_path / "user" / "Applications"
    for folder, names in ((system, ["Zoom.app", "notes.txt"]), (user, ["Zoom.app", "Raycast.app"])):
        folder.mkdir(parents=True)
        for name in names:
            (folder / name).mkdir()

    apps = scan_applications([str(system), str(user), str(tmp_path / "missing")])

    assert apps == {"Zoom": str(system), "Raycast": str(user)}
