"""Main module."""

import io
import PIL

from PIL import ImageFont, ImageDraw, Image

import Vision

try:
    import matplotlib
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


def pil2buf(pil_image):
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
    y1 = (1 - y) * im_height

    x2 = x1 + w * im_width
    y2 = y1 - h * im_height

    return x1, y1, x2, y2


def text_from_image(image, recognition_level="accurate", language_preference=None):
    """
    Helper function to call VNRecognizeTextRequest from Apple's vision framework.

    Args:
        image (str or PIL image): Path to image or PIL image.
        recognition_level (str, optional): Recognition level. Defaults to 'accurate'.
        language_preference (list, optional): Language preference. Defaults to None.

    Returns:
        list: List of tuples containing the text, the confidence and the bounding box.
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

    req = Vision.VNRecognizeTextRequest.alloc().init().autorelease()

    if recognition_level == "fast":
        req.setRecognitionLevel_(1)
    else:
        req.setRecognitionLevel_(0)

    if language_preference is not None:
        req.setRecognitionLanguages_(language_preference)

    handler = (
        Vision.VNImageRequestHandler.alloc()
        .initWithData_options_(pil2buf(image), None)
        .autorelease()
    )
    success = handler.performRequests_error_([req], None)

    res = []
    if success:
        for result in req.results():

            bbox = result.boundingBox()
            w, h = bbox.size.width, bbox.size.height
            x, y = bbox.origin.x, bbox.origin.y

            res.append((result.text(), result.confidence(), [x, y, w, h]))

    return res


class OCR:
    def __init__(self, image, recognition_level="accurate", language_preference=None):
        """OCR class to extract text from images.

        Args:
            image (str or PIL image): Path to image or PIL image.
            recognition_level (str, optional): Recognition level. Defaults to 'accurate'.
            language_preference (list, optional): Language preference. Defaults to None.

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
        self.res = None

    def recognize(self):

        res = text_from_image(
            self.image, self.recognition_level, self.language_preference
        )
        self.res = res

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

    def annotate_PIL(self, color="red", fontsize=12):
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
        font = ImageFont.truetype("Arial.ttf", fontsize)

        for _ in self.res:
            text, conf, bbox = _
            x1, y1, x2, y2 = convert_coordinates_pil(
                bbox, annotated_image.width, annotated_image.height
            )
            draw.rectangle((x1, y1, x2, y2), outline=color)
            draw.text((x1, y1), text, font=font, align="left", fill=color)

        return annotated_image
