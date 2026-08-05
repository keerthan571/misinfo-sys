print("OCR SERVICE LOADED")

import io
import re
import pytesseract

from PIL import Image, ImageEnhance, ImageFilter


pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


class OCRService:

    def __init__(self):
        pass


    def preprocess_image(self, image):

        image = image.convert("L")

        image = image.resize(
            (
                image.width * 4,
                image.height * 4
            )
        )

        image = ImageEnhance.Contrast(image).enhance(2)

        image = ImageEnhance.Sharpness(image).enhance(3)

        image = image.filter(
            ImageFilter.SHARPEN
        )

        return image



    def crop_engagement_area(self, image):

        width, height = image.size

        return image.crop(
            (
                0,
                int(height * 0.55),
                width,
                height
            )
        )



    def extract_numbers(self, image):

        values = []

        for psm in [6, 11]:

            data = pytesseract.image_to_data(
                image,
                config=f"--psm {psm}",
                output_type=pytesseract.Output.DICT
            )


            for i, text in enumerate(data["text"]):

                value = re.sub(
                    r"[^\d.kKmM]",
                    "",
                    text
                )


                if value and re.search(r"\d", value):

                    values.append(
                        {
                            "value": value,
                            "x": data["left"][i],
                            "y": data["top"][i]
                        }
                    )


        return values



    def order_engagement(self, values, image):

        # left to right order
        values.sort(
            key=lambda x: x["x"]
        )


        order = [
            "likes",
            "comments",
            "reposts",
            "shares",
            "bookmarks"
        ]


        result = {}

        used = set()

        index = 0


        for item in values:

            value = item["value"]


            # remove duplicate OCR readings
            if value in used:
                continue


            used.add(value)


            if index < len(order):

                result[order[index]] = value

                index += 1



        return result



    def clean_text(self, text):

        text = re.sub(
            r"[^\w\s.,!?@#%:/\-]",
            " ",
            text
        )

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text.strip()



    def extract_text_from_image(self, image_bytes):

        try:

            image = Image.open(
                io.BytesIO(image_bytes)
            )


            full_image = self.preprocess_image(
                image
            )


            engagement_image = self.crop_engagement_area(
                image
            )


            engagement_image = self.preprocess_image(
                engagement_image
            )


            raw_text = pytesseract.image_to_string(
                full_image,
                config="--psm 6"
            )


            numbers = self.extract_numbers(
                engagement_image
            )


            ordered_values = self.order_engagement(
                numbers,
                image
            )


            cleaned = self.clean_text(
                raw_text
            )


            print("========== OCR VALUES ==========")
            print(ordered_values)
            print("================================")


            return {

                "status": "success",

                "extracted_text": cleaned,

                "post_text": cleaned,

                "engagement_text": "",

                "ordered_values": ordered_values,

                "raw_text": raw_text,

                "confidence": 90,

                "word_count": len(cleaned.split()),

                "language": "Unknown",

                "ready_for_analysis": True

            }


        except Exception as e:

            return {

                "status": "error",

                "message": str(e)

            }



ocr_service = OCRService()