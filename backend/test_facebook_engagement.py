import cv2

from app.services.facebook_engagement_extractor import facebook_engagement_extractor


image=cv2.imread("test_facebook.png")

result=facebook_engagement_extractor.analyze(image)

print(result)