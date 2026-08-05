from fastapi import APIRouter, Depends, HTTPException
from app.auth.dependencies import get_current_user
from app.database.mongodb import analyses_collection


router = APIRouter()


@router.get("/")
async def get_history(
    current_user=Depends(get_current_user),
):

    analyses = []

    cursor = analyses_collection.find(
        {
            "email": current_user["email"]
        },
        {
            "_id": 0
        }
    ).sort(
        "analysis_time",
        -1
    )


    for item in cursor:

        analyses.append(item)


    return {

        "status": "success",

        "count": len(analyses),

        "history": analyses

    }




@router.get("/{analysis_id}")
async def get_single_history(

    analysis_id: str,

    current_user=Depends(get_current_user),

):


    analysis = analyses_collection.find_one(

        {
            "analysis_id": analysis_id,

            "email": current_user["email"]

        },

        {
            "_id": 0
        }

    )


    if not analysis:

        raise HTTPException(

            status_code=404,

            detail="Analysis not found"

        )


    return {

        "status": "success",

        "analysis": analysis

    }