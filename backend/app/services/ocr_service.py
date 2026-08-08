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

        image = image.convert(
            "L"
        )


        image = image.resize(
            (
                image.width * 4,
                image.height * 4
            )
        )


        image = ImageEnhance.Contrast(
            image
        ).enhance(2)



        image = ImageEnhance.Sharpness(
            image
        ).enhance(3)



        image = image.filter(
            ImageFilter.SHARPEN
        )


        return image






    def clean_text(self,text):

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






    def extract_text_from_image(self,image_bytes):


        try:


            image = Image.open(
                io.BytesIO(image_bytes)
            )



            processed = self.preprocess_image(
                image
            )



            raw_text = pytesseract.image_to_string(
                processed,
                config="--psm 6"
            )



            cleaned = self.clean_text(
                raw_text
            )



            return {

                "status":"success",

                "extracted_text":cleaned,

                "post_text":cleaned,

                "engagement_text":"",

                "ordered_values":{},


                "raw_text":raw_text,


                "confidence":90,


                "word_count":len(
                    cleaned.split()
                ),


                "language":"Unknown",


                "ready_for_analysis":True

            }



        except Exception as e:


            return {

                "status":"error",

                "message":str(e)

            }





ocr_service = OCRService()