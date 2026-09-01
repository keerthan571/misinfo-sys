import cv2

from app.services.engagement_extractor import (
    engagement_extractor
)


IMAGE_PATH = r"C:\Users\Keerthan\OneDrive\Desktop\photo\inst3.jpeg"


# ============================================================
# LOAD IMAGE
# ============================================================

image = cv2.imread(IMAGE_PATH)

if image is None:
    print("ERROR: Could not load image")
    raise SystemExit(1)


height, width = image.shape[:2]

print("\n==============================")
print("STARTING INSTAGRAM ENGAGEMENT TEST")
print("==============================\n")

print(f"IMAGE SIZE: {width} x {height}")
print(f"CHANNELS: {image.shape[2] if len(image.shape) == 3 else 1}")


# ============================================================
# DEBUG: INSTAGRAM REEL ENGAGEMENT AREA
# ============================================================

debug_image = image.copy()

# Instagram Reel action buttons are normally on the right side.
# Keep a broad right-side region for debugging.
x1 = int(width * 0.70)
x2 = width
y1 = int(height * 0.50)
y2 = int(height * 0.98)

cv2.rectangle(
    debug_image,
    (x1, y1),
    (x2 - 1, y2 - 1),
    (0, 255, 0),
    2
)

cv2.putText(
    debug_image,
    "INSTAGRAM REEL ENGAGEMENT AREA",
    (x1 - 180, y1 - 10),
    cv2.FONT_HERSHEY_SIMPLEX,
    0.55,
    (0, 255, 0),
    2
)

DEBUG_PATH = r"C:\Users\Keerthan\OneDrive\Desktop\photo\inst3_debug.jpg"

cv2.imwrite(DEBUG_PATH, debug_image)

print(f"\nDEBUG IMAGE SAVED:")
print(DEBUG_PATH)


# ============================================================
# RUN EXTRACTOR
# ============================================================

result = engagement_extractor.analyze(
    image,
    platform="Instagram"
)


# ============================================================
# RESULT
# ============================================================

print("\n==============================")
print("RESULT")
print("==============================")

print(result)

print("\n==============================")
print("EXPECTED INSTAGRAM REEL")
print("==============================")

print("likes     = 3238")
print("comments  = 6")
print("reposts   = 46")
print("shares    = 290")
print("bookmarks = 471")

print("\n==============================")
print("TEST COMPLETE")
print("==============================\n")