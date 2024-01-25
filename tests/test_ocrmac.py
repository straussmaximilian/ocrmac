#!/usr/bin/env python

"""Tests for `ocrmac` package."""
from tempfile import TemporaryFile
from unittest import TestCase

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


class Test(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Uncomment these to regenerate test output files
        # with open("test_output_fast.png", "w+b") as fast, open(
        #     "test_output_accurate.png", "w+b"
        # ) as accurate:
        #     ocrmac.OCR("test.png", recognition_level="fast").annotate_PIL().save(
        #         fast, format="png"
        #     )
        #     ocrmac.OCR("test.png", recognition_level="accurate").annotate_PIL().save(
        #         accurate, format="png"
        #     )

    def test_ocrmac(self):
        samples = {
            "GitHub: Let's build from here • X",
            "github.com",
            "Let's build from here",
            "Harnessed for productivity. Designed for collaboration.",
            "Celebrated for built-in security. Welcome to the",
            "platform developers love.",
            "Email address",
            "Sign up for GitHub",
            "Start a free enterprise trial >",
            "Trusted by the world's leading organizations y",
            "Mercedes-Benz",
        }

        annotations = {
            str(_[0])
            for _ in ocrmac.OCR("test.png", recognition_level="accurate").recognize()
        }
        self.assertTrue(samples <= annotations)

    def test_fast(self):
        annotated = ocrmac.OCR("test.png", recognition_level="fast").annotate_PIL()
        with TemporaryFile() as output2:
            annotated.save(output2, format="png")
            output2.seek(0)
            with open("test_output_fast.png", "rb") as output:
                self.assertEqual(output.read(), output2.read())

    def test_accurate(self):
        annotated = ocrmac.OCR("test.png", recognition_level="accurate").annotate_PIL()
        with TemporaryFile() as output2:
            annotated.save(output2, format="png")
            output2.seek(0)
            with open("test_output_accurate.png", "rb") as output:
                self.assertEqual(output.read(), output2.read())
