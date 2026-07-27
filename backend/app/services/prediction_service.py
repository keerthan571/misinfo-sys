import numpy as np
from sklearn.linear_model import LinearRegression



class PredictionService:


    def __init__(self):


        # Training examples
        # Features:
        # likes, shares, comments, views, bookmarks, spread_score, risk_score


        self.X = np.array([

            [100,20,10,1000,5,10,20],

            [500,100,50,5000,20,30,30],

            [1000,250,100,15000,50,50,40],

            [5000,1000,500,50000,200,75,60],

            [10000,3000,1000,150000,500,95,80]

        ])



        # Expected reach

        self.y = np.array([

            2000,

            8000,

            20000,

            70000,

            200000

        ])




        self.model = LinearRegression()


        self.model.fit(

            self.X,

            self.y

        )






    def calculate_risk_level(self, reach):


        if reach >= 100000:

            return "Very High"


        elif reach >= 50000:

            return "High"


        elif reach >= 10000:

            return "Medium"


        else:

            return "Low"








    def predict_spread(self, features):


        likes = features.get(
            "likes",
            0
        ) or 0



        shares = features.get(
            "shares",
            0
        ) or 0



        comments = features.get(
            "comments",
            0
        ) or 0



        views = features.get(
            "views",
            0
        ) or 0



        bookmarks = features.get(
            "bookmarks",
            0
        ) or 0



        spread_score = features.get(
            "spread_score",
            0
        ) or 0



        risk_score = features.get(
            "risk_score",
            0
        ) or 0





        input_data = np.array([[


            likes,

            shares,

            comments,

            views,

            bookmarks,

            spread_score,

            risk_score


        ]])







        predicted_reach = self.model.predict(

            input_data

        )[0]



        predicted_reach = max(

            predicted_reach,

            0

        )






        risk = self.calculate_risk_level(

            predicted_reach

        )






        virality_score = min(

            round(

                (

                    predicted_reach /

                    200000

                ) * 100,

                2

            ),

            100

        )







        if shares > likes:


            reason = (

                "High redistribution activity detected. "
                "Shares/reposts indicate strong propagation potential."

            )


        elif spread_score >= 50:


            reason = (

                "Multiple engagement signals indicate "
                "moderate to high spread probability."

            )


        elif risk_score >= 70:


            reason = (

                "Content has high-risk language patterns "
                "that may increase viral behaviour."

            )


        else:


            reason = (

                "Limited spread indicators detected "
                "from available engagement data."

            )







        return {


            "status":"success",


            "module":"Spread Prediction",




            "data":{


                "features_used":{


                    "likes":likes,

                    "shares":shares,

                    "comments":comments,

                    "views":views,

                    "bookmarks":bookmarks,

                    "spread_score":spread_score,

                    "risk_score":risk_score


                },



                "predicted_reach":round(

                    predicted_reach,

                    2

                ),



                "risk_level":risk,



                "virality_score":virality_score


            },



            "analysis_summary":reason


        }






prediction_service = PredictionService()