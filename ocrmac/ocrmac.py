"""Main module."""

import io
import objc

from PIL import ImageFont, ImageDraw, Image

import sys 

if sys.version_info < (3, 9):
    from typing import List, Dict, Set, Tuple
else:
    List, Tuple = list, tuple

import Vision

try:
    import matplotlib
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


def pil2buf(pil_image: Image.Image):
    """Convert PIL image to buffer"""
    buffer = io.BytesIO()
    pil_image.save(buffer, format="PNG")
    return buffer.getvalue()


def convert_coordinates_pyplot(bbox, im_width, im_height):
    """Convert vision coordinates to matplotlib coordinates"""
    x, y, w, h = bbox
    x1 = x * im_width
    y1 = (1 - y) * im_height

    x2 = w * im_width
    y2 = -h * im_height
    return x1, y1, x2, y2


def convert_coordinates_pil(bbox, im_width, im_height):
    """Convert vision coordinates to PIL coordinates"""
    x, y, w, h = bbox
    x1 = x * im_width
    y2 = (1 - y) * im_height

    x2 = x1 + w * im_width
    y1 = y2 - h * im_height

    return x1, y1, x2, y2


def text_from_image(
    image, recognition_level="accurate", language_preference=None, confidence_threshold=0.0
) -> List[Tuple[str, float, Tuple[float, float, float, float]]]:
    """
    Helper function to call VNRecognizeTextRequest from Apple's vision framework.

    :param image: Path to image (str) or PIL Image.Image.
    :param recognition_level: Recognition level. Defaults to 'accurate'.
    :param language_preference: Language preference. Defaults to None.
    :param confidence_threshold: Confidence threshold. Defaults to 0.0.

    :returns: List of tuples containing the text, the confidence and the bounding box.
        Each tuple looks like (text, confidence, (x, y, width, height))
        The bounding box (x, y, width, height) is composed of numbers between 0 and 1,
        that represent a percentage from total image (width, height) accordingly.
        You can use the `convert_coordinates_*` functions to convert them to pixels.
        For more info, see https://developer.apple.com/documentation/vision/vndetectedobjectobservation/2867227-boundingbox?language=objc
        and https://developer.apple.com/documentation/vision/vnrectangleobservation?language=objc
    """

    if isinstance(image, str):
        image = Image.open(image)
    elif not isinstance(image, Image.Image):
        raise ValueError("Invalid image format. Image must be a path or a PIL image.")

    if recognition_level not in {"accurate", "fast"}:
        raise ValueError(
            "Invalid recognition level. Recognition level must be 'accurate' or 'fast'."
        )

    if language_preference is not None and not isinstance(language_preference, list):
        raise ValueError(
            "Invalid language preference format. Language preference must be a list."
        )

    with objc.autorelease_pool():
        req = Vision.VNRecognizeTextRequest.alloc().init()

        if recognition_level == "fast":
            req.setRecognitionLevel_(1)
        else:
            req.setRecognitionLevel_(0)



        if language_preference is not None:
            
            available_languages = req.supportedRecognitionLanguagesAndReturnError_(None)[0]

            if not set(language_preference).issubset(set(available_languages)):
                raise ValueError(
                    f"Invalid language preference. Language preference must be a subset of {available_languages}."
                )
            req.setRecognitionLanguages_(language_preference)

        handler = Vision.VNImageRequestHandler.alloc().initWithData_options_(
            pil2buf(image), None
        )

        success = handler.performRequests_error_([req], None)
        res = []
        if success:
            for result in req.results():
                bbox = result.boundingBox()
                w, h = bbox.size.width, bbox.size.height
                x, y = bbox.origin.x, bbox.origin.y

                if result.confidence() >= confidence_threshold:
                    res.append((result.text(), result.confidence(), [x, y, w, h]))

        return res


class OCR:
    def __init__(self, image, recognition_level="accurate", language_preference=None, confidence_threshold=0.0):
        """OCR class to extract text from images.

        Args:
            image (str or PIL image): Path to image or PIL image.
            recognition_level (str, optional): Recognition level. Defaults to 'accurate'.
            language_preference (list, optional): Language preference. Defaults to None.
            param confidence_threshold: Confidence threshold. Defaults to 0.0.

        """

        if isinstance(image, str):
            image = Image.open(image)
        elif not isinstance(image, Image.Image):
            raise ValueError(
                "Invalid image format. Image must be a path or a PIL image."
            )

        self.image = image
        self.recognition_level = recognition_level
        self.language_preference = language_preference
        self.confidence_threshold = confidence_threshold
        self.res = None

    def recognize(
        self, px=False
    ) -> List[Tuple[str, float, Tuple[float, float, float, float]]]:
        res = text_from_image(
            self.image, self.recognition_level, self.language_preference, self.confidence_threshold
        )
        self.res = res
        
        if px:
            return [(text, conf, convert_coordinates_pil(bbox, self.image.width, self.image.height)) for text, conf, bbox in res]

        else:
            return res

    def annotate_matplotlib(
        self, figsize=(20, 20), color="red", alpha=0.5, fontsize=12
    ):
        """_summary_

        Args:
            figsize (tuple, optional): _description_. Defaults to (20,20).
            color (str, optional): _description_. Defaults to 'red'.
            alpha (float, optional): _description_. Defaults to 0.5.
            fontsize (int, optional): _description_. Defaults to 12.

        Returns:
            _type_: _description_

        """
        if not MATPLOTLIB_AVAILABLE:
            raise ImportError(
                "Matplotlib is not available. Please install matplotlib to use this feature."
            )

        if self.res is None:
            self.recognize()

        fig, ax = plt.subplots(figsize=figsize)
        ax.imshow(self.image, alpha=alpha)
        for _ in self.res:
            text, conf, bbox = _
            x1, y1, x2, y2 = convert_coordinates_pyplot(
                bbox, self.image.width, self.image.height
            )
            rect = patches.Rectangle(
                (x1, y1), x2, y2, linewidth=1, edgecolor=color, facecolor="none"
            )
            plt.text(x1, y1, text, fontsize=fontsize, color=color)
            ax.add_patch(rect)

        return fig

    def annotate_PIL(self, color="red", fontsize=12) -> Image.Image:
        """_summary_

        Args:
            color (str, optional): _description_. Defaults to 'red'.
            fontsize (int, optional): _description_. Defaults to 12.

        Returns:
            _type_: _description_
        """

        annotated_image = self.image.copy()

        if self.res is None:
            self.recognize()

        draw = ImageDraw.Draw(annotated_image)
        font = ImageFont.truetype("Arial Unicode.ttf", fontsize)

        for text, conf, bbox in self.res:
            x1, y1, x2, y2 = convert_coordinates_pil(
                bbox, annotated_image.width, annotated_image.height
            )
            draw.rectangle((x1, y1, x2, y2), outline=color)
            draw.text((x1, y2), text, font=font, align="left", fill=color)

        return annotated_image
