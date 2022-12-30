#!/usr/bin/env python

"""Tests for `ocrmac` package."""

import pytest

#from click.testing import CliRunner

from ocrmac import ocrmac
#from ocrmac import cli


@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument."""
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string


def test_command_line_interface():
    pass
    
    """Test the CLI."""
    """
    runner = CliRunner()
    result = runner.invoke(cli.main)
    assert result.exit_code == 0
    assert "ocrmac.cli.main" in result.output
    help_result = runner.invoke(cli.main, ["--help"])
    assert help_result.exit_code == 0
    assert "--help  Show this message and exit." in help_result.output
    """


def test_ocrmac():

    samples = [
        "GitHub: Let's build from here",
        "github.com",
        "Let's build from here",
        "Harnessed for productivity. Designed for collaboration.",
        "Celebrated for built-in security. Welcome to the",
        "platform developers love.",
        "Email address",
        "Sign up for GitHub",
        "Start a free enterprise trial",
        "Trusted by the world's leading organizations",
        "Mercedes-Benz",
    ]

    annotations = [
        _[0] for _ in ocrmac.OCR("test.png", recognition_level="accurate").recognize()
    ]

    for sample in samples:
        found = False
        for annotation in annotations:
            if sample in annotation:
                found = True
                break
        assert found
