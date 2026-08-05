import cv2

from app.services.engagement_extractor import engagement_extractor


image = cv2.imread(
    "test_instagram.png"
)


result = engagement_extractor.analyze(
    image
)


print("RESULT:")
print(result)