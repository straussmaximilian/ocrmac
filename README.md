# ocrmac
A python wrapper to extract text from images on a mac system. Uses the vision framework from Apple. Simply pass a path to an image or a `PIL` image directly and get lists of texts, their confidence and bounding box.

This only works on macOS systems with newer macOS versions (10.15+).

## Example and Quickstart

Install via pip:

- `pip install ocrmac`

### Basic Usage

```python
    from ocrmac import ocrmac
    annotations = ocrmac.OCR('test.png').recognize()
    print(annotations)
```

Output (Text, Confidence, BoundingBox):

```
[("GitHub: Let's build from here - X", 0.5, [0.16, 0.91, 0.17, 0.01]),
('github.com', 0.5, [0.174, 0.87, 0.06, 0.01]),
('Qi &0 O M #O', 0.30, [0.65, 0.87, 0.23, 0.02]),
[...]
('P&G U TELUS', 0.5, [0.64, 0.16, 0.22, 0.03])]
```
(BoundingBox precision capped for readability reasons)

### Create Annotated Images

```python
    from ocrmac import ocrmac
    ocrmac.OCR('test.png').annotate_PIL()
```

![Plot](output.png)

## Functionality

- You can pass the path to an image or a PIL image as an object
- You can use as a class (`ocrmac.OCR`) or function `ocrmac.text_from_image`)
- You can pass several arguments:
    - recognition_level: `fast` or `accurate`
    - language_preference: A list with langages for post-processing, e.g. `['en', 'de']`
- You can get an annotated output either as PIL image (`annotate_PIL`) or matplotlib figure (`annotate_matplotlib`)


## Speed

Timings for the  above recognize-statement:
MacBook Pro (14-inch, 2021):
- `accurate`: 233 ms ± 1.77 ms per loop (mean ± std. dev. of 7 runs, 1 loop each)
- `fast`: 200 ms ± 4.7 ms per loop (mean ± std. dev. of 7 runs, 1 loop each)


## Technical Background & Motivation
If you want to do Optical character recognition (OCR) with Python, widely used tools are [`pytesseract`](https://github.com/madmaze/pytesseract) or [`EasyOCR`](https://github.com/JaidedAI/EasyOCR). For me, tesseract never did give great results. EasyOCR did, but it is slow con CPU. While GPU for CUDA, it is not for Mac.  However, as a mac user you might notice that you can, with newer versions, directly copy and paste from images. The built-in OCR functionality is quite good. The underlying functionality for this is [`VNRecognizeTextRequest`](https://developer.apple.com/documentation/vision/vnrecognizetextrequest) from Apple's Vision Framework. Unfortuantely it is in Swift, luckily, a wrapper for this exists. [`pyobjc-framework-Vision`](https://github.com/ronaldoussoren/pyobjc). `ocrmac` utilizes this wrapper and provides an easy interface to use this for OCR.

I found the following resources very helpful when implementing this:
- [Gist from RheTbull](https://gist.github.com/RhetTbull/1c34fc07c95733642cffcd1ac587fc4c)
- [Apple Documentation](https://developer.apple.com/documentation/vision/recognizing_text_in_images/)
- [Using Pythonista with VNRecognizeTextRequest](https://forum.omz-software.com/topic/6016/recognize-text-from-picture)


## Contributing

If you have a feature request or a bug report, please post it either as an idea in the discussions or as an issue on the GitHub issue tracker.  If you want to contribute, put a PR for it. You can find more guidelines for contributing and how to get started here. 

If you like the project, consider starring it!


