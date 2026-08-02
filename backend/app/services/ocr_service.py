import io
import re
import pytesseract
from PIL import Image,ImageEnhance,ImageFilter

pytesseract.pytesseract.tesseract_cmd=r"C:\Program Files\Tesseract-OCR\tesseract.exe"

class OCRService:

    def __init__(self):
        self.metric_patterns=[
            r"(\d+(?:\.\d+)?[kKmM]?)\s*(likes?|reactions?|comments?|replies?|shares?|reposts?|retweets?|views?|saves?|bookmarks?)",
            r"(likes?|reactions?|comments?|replies?|shares?|reposts?|retweets?|views?|saves?|bookmarks?)\s*[:\-]?\s*(\d+(?:\.\d+)?[kKmM]?)"
        ]

    def clean_text(self,text):

        text=text.replace("\r","")

        text=re.sub(
            r"[^\w\s.,!?@#%$₹:/\-]",
            " ",
            text
        )

        text=re.sub(
            r"[ ]{2,}",
            " ",
            text
        )

        text=re.sub(
            r"\n{3,}",
            "\n\n",
            text
        )

        lines=[]

        for line in text.split("\n"):

            line=line.strip()

            if len(line)<2:
                continue

            if re.fullmatch(r"[\W\d_]+",line):
                continue

            lines.append(line)

        return "\n".join(lines).strip()

    def preprocess_image(self,image):

        image=image.convert("L")

        image=image.resize(
            (
                image.width*3,
                image.height*3
            )
        )

        image=ImageEnhance.Contrast(image).enhance(2)

        image=ImageEnhance.Sharpness(image).enhance(3)

        image=image.filter(
            ImageFilter.SHARPEN
        )

        return image

    def extract_numbers(self,text):

        return re.findall(
            r"\d+(?:,\d+)*(?:\.\d+)?\s*[kKmM]?",
            text
        )

    def extract_engagement_text(self,text):

        lines=text.split("\n")

        engagement=[]
        content=[]

        for line in lines:

            found=False

            for pattern in self.metric_patterns:

                if re.search(
                    pattern,
                    line,
                    re.IGNORECASE
                ):
                    engagement.append(line)
                    found=True
                    break

            if not found:
                content.append(line)

        numbers=self.extract_numbers(text)

        if not engagement and len(numbers)>=3:

            engagement.append(
                " ".join(numbers[-5:])
            )

        return (
            "\n".join(content).strip(),
            "\n".join(engagement).strip()
        )

    def calculate_confidence(self,image):

        try:

            data=pytesseract.image_to_data(
                image,
                output_type=pytesseract.Output.DICT
            )

            values=[
                int(x)
                for x in data["conf"]
                if x!="-1" and int(x)>0
            ]

            if not values:
                return 0

            return int(
                sum(values)/len(values)
            )

        except:

            return 0

    def extract_text_from_image(self,image_bytes):

        if not image_bytes:

            return {
                "status":"error",
                "message":"No image provided."
            }

        try:

            image=Image.open(
                io.BytesIO(image_bytes)
            )

            image=self.preprocess_image(
                image
            )

            outputs=[]

            for config in [
                "--psm 6",
                "--psm 11",
                "--psm 12"
            ]:

                outputs.append(
                    pytesseract.image_to_string(
                        image,
                        config=config
                    )
                )

            raw_text="\n".join(outputs)

            print("========== OCR NUMBERS ==========")
            print(self.extract_numbers(raw_text))
            print("=================================")

            cleaned=self.clean_text(
                raw_text
            )

            post_text,engagement_text=self.extract_engagement_text(
                cleaned
            )

            confidence=self.calculate_confidence(
                image
            )

            return {
                "status":"success",
                "extracted_text":post_text,
                "post_text":post_text,
                "engagement_text":engagement_text,
                "raw_text":raw_text,
                "confidence":confidence,
                "word_count":len(post_text.split()),
                "language":"Unknown",
                "ready_for_analysis":bool(post_text)
            }

        except Exception as e:

            return {
                "status":"error",
                "message":"OCR processing failed.",
                "error":str(e)
            }

ocr_service=OCRService()