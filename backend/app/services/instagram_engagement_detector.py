import cv2
import numpy as np
import pytesseract
import re


class InstagramEngagementDetector:

    def detect(self,image):

        width,height=image.size

        engagement={
            "likes":0,
            "comments":0,
            "reposts":0,
            "shares":0,
            "bookmarks":0,
            "views":0,
            "metrics":[]
        }

        if height>width:

            crop=image.crop(
                (
                    int(width*0.55),
                    int(height*0.20),
                    width,
                    int(height*0.95)
                )
            )

            layout="reel"

        else:

            crop=image.crop(
                (
                    0,
                    int(height*0.70),
                    width,
                    height
                )
            )

            layout="post"


        values=[]


        for processed in self.preprocess(crop):

            data=pytesseract.image_to_data(
                processed,
                config="--psm 6",
                output_type=pytesseract.Output.DICT
            )


            for i,text in enumerate(data["text"]):

                value=re.sub(
                    r"[^\d.kKmM]",
                    "",
                    text
                )


                if value and re.search(r"\d",value):

                    values.append(
                        {
                            "value":value,
                            "x":data["left"][i],
                            "y":data["top"][i]
                        }
                    )


        values=self.remove_duplicates(values)


        # Instagram bottom row / right side icons are horizontal
        values.sort(
            key=lambda x:x["x"]
        )


        print("RAW OCR VALUES:",values)


        order=[
            "likes",
            "comments",
            "reposts",
            "shares",
            "bookmarks"
        ]


        index=0


        for item in values:

            if index>=len(order):
                break

            try:

                number=self.parse_number(
                    item["value"]
                )

                if number>0:

                    engagement[order[index]]=number
                    index+=1


            except:

                continue



        for key in [
            "likes",
            "comments",
            "reposts",
            "shares",
            "bookmarks"
        ]:

            if engagement[key]>0:

                engagement["metrics"].append(
                    {
                        "label":key.title(),
                        "value":engagement[key]
                    }
                )


        print("FINAL ENGAGEMENT:",engagement)


        return engagement



    def preprocess(self,image):

        gray=np.array(
            image.convert("L")
        )


        gray=cv2.resize(
            gray,
            None,
            fx=6,
            fy=6,
            interpolation=cv2.INTER_CUBIC
        )


        normal=cv2.threshold(
            gray,
            150,
            255,
            cv2.THRESH_BINARY
        )[1]


        inverted=cv2.threshold(
            gray,
            150,
            255,
            cv2.THRESH_BINARY_INV
        )[1]


        return [
            normal,
            inverted
        ]



    def remove_duplicates(self,values):

        result=[]

        seen=set()


        for item in values:

            key=item["value"]

            if key not in seen:

                result.append(item)
                seen.add(key)


        return result



    def parse_number(self,value):

        value=value.replace(",","").lower()


        if value.endswith("k"):

            return int(
                float(value[:-1])*1000
            )


        if value.endswith("m"):

            return int(
                float(value[:-1])*1000000
            )


        return int(float(value))



instagram_detector=InstagramEngagementDetector()