import cv2

from app.services.twitter_engagement_extractor import twitter_engagement_extractor


image = cv2.imread(
    "test_twitter.png"
)


result = twitter_engagement_extractor.analyze(
    image
)


print("TWITTER RESULT:")
print(result)