from planitout.beamer import beamer_template


def test_beamer_template(beamer_tex_file: str):
    with open(beamer_tex_file, "r") as f:
        expected_content = f.read()
    assert beamer_template() == expected_content
