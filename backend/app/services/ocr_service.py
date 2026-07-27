import io
import re

import pytesseract

from PIL import Image, ImageEnhance, ImageFilter


pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)



class OCRService:


    def clean_text(self, text):

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text.strip()



    def calculate_confidence(self, image):

        try:

            data = pytesseract.image_to_data(
                image,
                output_type=pytesseract.Output.DICT
            )


            confidence_values = []


            for conf in data["conf"]:

                if int(conf) > 0:

                    confidence_values.append(
                        int(conf)
                    )


            if confidence_values:

                return int(
                    sum(confidence_values)
                    /
                    len(confidence_values)
                )


            return 0


        except:

            return 0





    def extract_text_from_image(self, image_bytes: bytes):

        try:


            if not image_bytes:

                return {

                    "status":"error",

                    "message":
                    "No image provided."

                }




            image = Image.open(
                io.BytesIO(image_bytes)
            )



            image = image.convert(
                "L"
            )



            image = image.resize(

                (
                    image.width * 2,
                    image.height * 2
                )

            )



            enhancer = ImageEnhance.Contrast(
                image
            )


            image = enhancer.enhance(
                2
            )



            image = image.filter(
                ImageFilter.SHARPEN
            )





            config = "--psm 6"



            raw_text = pytesseract.image_to_string(

                image,

                config=config

            )



            cleaned_text = self.clean_text(
                raw_text
            )



            confidence = self.calculate_confidence(
                image
            )




            return {


                "status":"success",


                "extracted_text":
                cleaned_text,


                "confidence":
                confidence,


                "word_count":
                len(
                    cleaned_text.split()
                ),


                "language":
                "Unknown",


                "ready_for_analysis":

                True if cleaned_text else False


            }




        except Exception as e:


            return {


                "status":"error",


                "message":
                "OCR processing failed.",


                "error":
                str(e)

            }




ocr_service = OCRService()