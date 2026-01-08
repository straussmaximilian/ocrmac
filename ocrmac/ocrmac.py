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
import inspect

try:
    import matplotlib
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


try:
    from AppKit import NSData, NSImage
    from CoreFoundation import (
        CFRunLoopRunInMode,
        kCFRunLoopDefaultMode,
        CFRunLoopStop,
        CFRunLoopGetCurrent,
    )
    
    objc.registerMetaDataForSelector(
            b"VKCImageAnalyzer",
            b"processRequest:progressHandler:completionHandler:",
            {
                "arguments": {
                    3: {
                        "callable": {
                            "retval": {"type": b"v"},
                            "arguments": {
                                0: {"type": b"^v"},
                                1: {"type": b"d"},
                            },
                        }
                    },
                    4: {
                        "callable": {
                            "retval": {"type": b"v"},
                            "arguments": {
                                0: {"type": b"^v"},
                                1: {"type": b"@"},
                                2: {"type": b"@"},
                            },
                        }
                    },
                }
            },
        )
    
    LIVETEXT_AVAILABLE = True
except ImportError:
    LIVETEXT_AVAILABLE = False


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
    image, recognition_level="accurate", language_preference=None, confidence_threshold=0.0, detail = True
) -> List[Tuple[str, float, Tuple[float, float, float, float]]]:
    """
    Helper function to call VNRecognizeTextRequest from Apple's vision framework.

    :param image: Path to image (str) or PIL Image.Image.
    :param recognition_level: Recognition level. Defaults to 'accurate'.
    :param language_preference: Language preference. Defaults to None.
    :param confidence_threshold: Confidence threshold. Defaults to 0.0.
    :param detail: Whether to return the bounding box or not. Defaults to True.

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

        ret = handler.performRequests_error_([req], None)
        # PyObjC returns either a bool or a (bool, NSError|None) tuple depending on the signature mapping.
        if isinstance(ret, tuple):
            ok, err = ret
        else:
            ok, err = bool(ret), None
        res = []
        if ok and err is None:
            for result in req.results():
                confidence = result.confidence()
                if confidence >= confidence_threshold:
                    if detail:
                        bbox = result.boundingBox()
                        x, y = bbox.origin.x, bbox.origin.y
                        w, h = bbox.size.width, bbox.size.height
                        res.append((result.text(), confidence, [x, y, w, h]))
                    else:
                        res.append(result.text())
            
        return res


def livetext_from_image(image, language_preference=None, detail=True, unit='token'):
    """
    Helper function to call VKCImageAnalyzer from Apple's livetext framework.

    :param image: Path to image (str) or PIL Image.Image.
    :param language_preference: Language preference. Defaults to None.
    :param detail: Whether to return the bounding box or not. Defaults to True.
    :param unit: Output granularity for flat results. 'token' (default)
        returns the finest-grained children (often characters for CJK),
        'line' returns one entry per line (full line text and its bbox).

    :returns: List of tuples containing the text and the bounding box.
        Each tuple looks like (text, (x, y, width, height))
        The bounding box (x, y, width, height) is composed of numbers between 0 and 1,
        that represent a percentage from total image (width, height) accordingly.
        You can use the `convert_coordinates_*` functions to convert them to pixels.
        For more info, see https://developer.apple.com/documentation/vision/vndetectedobjectobservation/2867227-boundingbox?language=objc
        and https://developer.apple.com/documentation/vision/vnrectangleobservation?language=objc
    """

    if not LIVETEXT_AVAILABLE:
        raise ImportError(
            "Invalid framework selected, Livetext is not available. \
            Please makesure your system is running MacOS Sonoma or later, and essential packages are installed."
        )

    if isinstance(image, str):
        image = Image.open(image)
    elif not isinstance(image, Image.Image):
        raise ValueError("Invalid image format. Image must be a path or a PIL image.")

    if language_preference is not None and not isinstance(language_preference, list):
        raise ValueError(
            "Invalid language preference format. Language preference must be a list."
        )
    
    if unit not in {"token", "line"}:
        raise ValueError("Invalid unit. Must be 'token' or 'line'.")

    def pil2nsimage(pil_image: Image.Image):
        image_bytes = io.BytesIO()
        pil_image.save(image_bytes, format="TIFF")
        ns_data = NSData.dataWithBytes_length_(
            image_bytes.getvalue(), len(image_bytes.getvalue())
        )
        return NSImage.alloc().initWithData_(ns_data)

    result = []
    with objc.autorelease_pool():
        ns_image = pil2nsimage(image)

        # Initialize the image analyzer
        analyzer = objc.lookUpClass("VKCImageAnalyzer").alloc().init()
        request = (
            objc.lookUpClass("VKCImageAnalyzerRequest")
            .alloc()
            .initWithImage_requestType_(ns_image, 1)  # VKAnalysisTypeText
        )

        # Set the language preference
        if language_preference is not None:
            request.setLocales_(language_preference)

        # Analysis callback functions
        def process_handler(analysis, error):
            if error:
                raise RuntimeError("Error during analysis: " + str(error))
            else:
                lines = analysis.allLines()
                if lines:
                    for line in lines:
                        if unit == 'line':
                            line_text = line.string()
                            if detail:
                                bounding_box = line.quad().boundingBox()
                                x, y = bounding_box.origin.x, bounding_box.origin.y
                                w, h = bounding_box.size.width, bounding_box.size.height
                                y = 1 - y - h  # align with Vision coordinate system
                                result.append((line_text, 1.0, [x, y, w, h]))
                            else:
                                result.append(line_text)
                        else:
                            for char in line.children():
                                char_text = char.string()
                                if detail:
                                    bounding_box = char.quad().boundingBox()
                                    x, y = bounding_box.origin.x, bounding_box.origin.y
                                    w, h = bounding_box.size.width, bounding_box.size.height
                                    # More process on y, it differs from the vision framework
                                    y = 1 - y - h
                                    result.append((char_text, 1.0, [x, y, w, h]))
                                else:
                                    result.append(char_text)

                CFRunLoopStop(CFRunLoopGetCurrent())

        # Do the analysis
        analyzer.processRequest_progressHandler_completionHandler_(
            request, lambda progress: None, process_handler
        )

        # Loops until the OCR is completed
        CFRunLoopRunInMode(kCFRunLoopDefaultMode, 10.0, False)

    return result


class OCR:
    def __init__(self, image, framework="vision", recognition_level="accurate", language_preference=None, confidence_threshold=0.0, detail=True, unit='token'):
        """OCR class to extract text from images.

        Args:
            image (str or PIL image): Path to image or PIL image.
            framework (str, optional): Framework to use. Defaults to 'vision'.
            recognition_level (str, optional): Recognition level. Defaults to 'accurate'.
            language_preference (list, optional): Language preference. Defaults to None.
            param confidence_threshold: Confidence threshold. Defaults to 0.0.
            detail (bool, optional): Whether to return the bounding box or not. Defaults to True.
            unit (str, optional): LiveText-only flat output granularity.
                'token' (default) returns fine-grained children, 'line' returns
                one entry per line. Ignored for Vision.
        """

        if isinstance(image, str):
            image = Image.open(image)
        elif not isinstance(image, Image.Image):
            raise ValueError(
                "Invalid image format. Image must be a path or a PIL image."
            )
        
        if framework not in {"vision", "livetext"}:
            raise ValueError("Invalid framework selected. Framework must be 'vision' or 'livetext'.")
        
        if framework == 'livetext':
            sig = inspect.signature(self.__init__)

            default_recognition_level = sig.parameters['recognition_level'].default
            default_confidence_threshold = sig.parameters['confidence_threshold'].default

            if recognition_level != default_recognition_level:
                raise ValueError(f"Recognition level is not supported for Livetext framework. Please use the default value `{default_recognition_level}` or don't pass an argument.")
            if confidence_threshold != default_confidence_threshold:
                raise ValueError(f"Confidence threshold is not supported for Livetext framework. Please use the default value `{default_confidence_threshold}` or don't pass an argument.")
            
            if unit not in {"token", "line"}:
                raise ValueError("Invalid unit. Must be 'token' or 'line'.")

        self.image = image
        self.framework = framework
        self.recognition_level = recognition_level
        self.language_preference = language_preference
        self.confidence_threshold = confidence_threshold
        self.res = None
        self.detail = detail
        self.unit = unit

    def recognize(
        self, px=False
    ) -> List[Tuple[str, float, Tuple[float, float, float, float]]]:
        if self.framework == "vision":
            res = text_from_image(
                self.image, self.recognition_level, self.language_preference, self.confidence_threshold, detail=self.detail
            )
        elif self.framework == "livetext":
            res = livetext_from_image(
                self.image, self.language_preference, detail=self.detail, unit=self.unit
            )
        else:
            raise ValueError("Invalid framework selected. Framework must be 'vision' or 'livetext'.")

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
        
        if not self.detail:
            raise ValueError("Please set detail=True to use this feature.")

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
        
        if not self.detail:
            raise ValueError("Please set detail=True to use this feature.")

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
