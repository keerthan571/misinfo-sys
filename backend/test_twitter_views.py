import cv2
from app.services.twitter_views_detector import twitter_views_detector


image=cv2.imread(
    "test_twitter.png"
)


result=twitter_views_detector.detect(
    image
)


print(
    "VIEW RESULT:",
    result
)