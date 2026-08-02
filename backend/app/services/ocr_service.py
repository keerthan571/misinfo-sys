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


    def crop_engagement_area(self,image):

        width,height=image.size

        return image.crop(
            (
                0,
                int(height*0.85),
                width,
                height
            )
        )


    def extract_engagement_order(self,image):

        data=pytesseract.image_to_data(
            image,
            config="--psm 6",
            output_type=pytesseract.Output.DICT
        )

        numbers=[]

        for i,text in enumerate(data["text"]):

            value=re.sub(
                r"[^\d.kKmM]",
                "",
                text
            )

            if value and re.search(r"\d",value):

                numbers.append(
                    {
                        "x":data["left"][i],
                        "value":value
                    }
                )

        numbers.sort(
            key=lambda x:x["x"]
        )

        values=[
            item["value"]
            for item in numbers
        ]

        print("ORDER VALUES:",values)

        return values


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


            engagement_image=self.crop_engagement_area(
                image
            )


            image=self.preprocess_image(
                image
            )

            engagement_image=self.preprocess_image(
                engagement_image
            )
            engagement_image=ImageEnhance.Contrast(
                engagement_image
            ).enhance(3)


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

            engagement_raw=pytesseract.image_to_string(
                engagement_image,
                config="--psm 11"
            )


            print("========== OCR NUMBERS ==========")
            print(self.extract_engagement_order(engagement_image))
            print("=================================")


            cleaned=self.clean_text(
                raw_text
            )


            post_text,_=self.extract_engagement_text(
                cleaned
            )


            confidence=self.calculate_confidence(
                image
            )


            return {
                "status":"success",
                "extracted_text":post_text,
                "post_text":post_text,
                "engagement_text":engagement_raw,
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