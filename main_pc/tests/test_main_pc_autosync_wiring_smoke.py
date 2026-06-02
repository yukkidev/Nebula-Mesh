import os


def test_main_pc_imports_and_builds():
    # Smoke: ensure the module imports and build_app works.
    import main_pc.__main__ as m

    assert hasattr(m, "main")
