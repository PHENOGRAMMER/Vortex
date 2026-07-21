from fastapi import APIRouter
from fastapi import HTTPException

from backend.providers.factory import ProviderFactory

router = APIRouter()


@router.get("/")
async def providers():

    response = []

    for provider in ProviderFactory.list():

        response.append({

            "id": provider.id,

            "name": provider.name,

            **provider.capabilities,

        })

    return response


@router.get("/models")
async def provider_models(provider: str):

    try:

        instance = ProviderFactory.get(provider)

    except ValueError as e:

        raise HTTPException(

            status_code=404,

            detail=str(e),

        )

    return await instance.list_models()