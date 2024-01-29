#!/usr/bin/env python

"""Tests for `ocrmac` package."""
from tempfile import TemporaryFile
from unittest import TestCase
import os 
from PIL import Image, ImageChops
import math 

import pytest

#from click.testing import CliRunner

from ocrmac import ocrmac
#from ocrmac import cli

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))


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

def rms_difference(image1, image2):
    """Calculate the root-mean-square difference between two images."""
    # Convert images to the same size and format
    image1 = image1.convert('RGB').resize((256, 256))
    image2 = image2.convert('RGB').resize((256, 256))

    # Calculate the difference between images
    diff = ImageChops.difference(image1, image2)

    # Calculate the RMS
    h = diff.histogram()
    sq = (value * ((idx % 256) ** 2) for idx, value in enumerate(h))
    sum_of_squares = sum(sq)
    rms = math.sqrt(sum_of_squares / float(image1.size[0] * image1.size[1]))

    return rms


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
            "Let's build from here",
            "github.com",
            "Let's build from here",
            "Harnessed for productivity. Designed for collaboration.",
            "Celebrated for built-in security. Welcome to the",
            "platform developers love.",
            "Email address",
            "Sign up for GitHub",
            "Trusted by the world's leading organizations y",
            "Mercedes-Benz",
        }

        annotations = {
            str(_[0])
            for _ in ocrmac.OCR(os.path.join(THIS_FOLDER, "test.png"), recognition_level="accurate", language_preference=['en-US']).recognize()
        }
        print(annotations)

        for _ in samples:
            self.assertIn(_, annotations)

    def test_fast(self):
        annotated = ocrmac.OCR(os.path.join(THIS_FOLDER, "test.png"), recognition_level="fast", language_preference=['en-US'],  confidence_threshold=1.0).annotate_PIL()
        ref_image = Image.open(os.path.join(THIS_FOLDER, "test_output_fast.png"))
        rms = rms_difference(annotated, ref_image)

        assert rms < 5.0
    
    def test_accurate(self):
        annotated = ocrmac.OCR(os.path.join(THIS_FOLDER, "test.png"), recognition_level="accurate", language_preference=['en-US'],  confidence_threshold=1.0).annotate_PIL()
        ref_image = Image.open(os.path.join(THIS_FOLDER, "test_output_accurate.png"))
        rms = rms_difference(annotated, ref_image)

        assert rms < 5.0