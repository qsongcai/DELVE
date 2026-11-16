#!/usr/bin/env python3
"""Build the compressed manuscript from compressed_md into manuscript_compressed."""
import os
import build_manuscript as bm

ROOT = bm.ROOT
bm.SRC = os.path.join(ROOT, "compressed_md")
bm.BUILD = os.path.join(ROOT, "manuscript_compressed")

if __name__ == "__main__":
    bm.main()
