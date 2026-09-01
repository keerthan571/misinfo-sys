import cv2

from app.services.engagement_extractor import (
    engagement_extractor
)


IMAGE_PATH = r"C:\Users\Keerthan\OneDrive\Desktop\photo\WhatsApp Image 2026-08-08 at 4.48.22 PM.jpeg"


image = cv2.imread(
    IMAGE_PATH
)


if image is None:
    print("ERROR: Could not load image")
    raise SystemExit(1)


print("\n==============================")
print("STARTING ENGAGEMENT TEST")
print("==============================\n")


result = engagement_extractor.analyze(
    image
)


print("\n==============================")
print("RESULT")
print("==============================")

print(result)