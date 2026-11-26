# Entry program for news-image-20261126 (Python 3.13, standard library only).
#
# The image is entry.png beside this file, rendered by render.py in this
# repository with real fonts (EB Garamond and Playfair Display, SIL OFL,
# see fonts/OFL.txt). This program only copies those exact bytes to
# /output/entry.png, so the grader's two runs write identical output.
#
# Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
#   mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py

import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")

os.makedirs(OUT, exist_ok=True)
shutil.copyfile(
    os.path.join(HERE, "entry.png"),
    os.path.join(OUT, "entry.png"),
)
print("wrote", os.path.join(OUT, "entry.png"))
