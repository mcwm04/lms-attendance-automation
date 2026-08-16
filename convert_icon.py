"""
Run this once to convert assets/wizard_small.bmp into a proper
.ico file with the standard sizes Windows expects for title
bar / taskbar / Alt-Tab icons.

Requires Pillow:  pip install pillow
"""

from pathlib import Path
from PIL import Image

SOURCE = Path("assets/wizard_small.bmp")
DEST = Path("assets/wizard_small.ico")

if __name__ == "__main__":

    img = Image.open(SOURCE).convert("RGBA")

    img.save(
        DEST,
        format="ICO",
        sizes=[(16, 16), (32, 32), (48, 48), (256, 256)],
    )

    print(f"✓ Wrote {DEST}")
