import os

from tavily import TavilyClient
from dotenv import load_dotenv


load_dotenv()


tavily_client = TavilyClient(
    api_key=os.getenv("TAVILY_API_KEY")
)



class TavilyService:


    def search_claim(self, claim, keywords=None):

        try:

            if not claim:

                return {
                    "status":"error",
                    "message":"No claim provided."
                }



            query = claim


            if keywords:

                query += " " + " ".join(keywords[:5])



            response = tavily_client.search(

                query=query,

                search_depth="advanced",

                max_results=5

            )



            results = []


            for item in response.get("results", []):

                results.append({

                    "title":
                    item.get(
                        "title",
                        ""
                    ),

                    "url":
                    item.get(
                        "url",
                        ""
                    ),

                    "content":
                    item.get(
                        "content",
                        ""
                    )

                })



            return {

                "status":"success",

                "query":query,

                "results":results

            }



        except Exception as e:


            return {

                "status":"error",

                "message":str(e)

            }





tavily_service = TavilyService()