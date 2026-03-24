from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["api"])


# Example request/response models
class ExampleRequest(BaseModel):
    name: str
    value: Optional[int] = None


class ExampleResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    message: Optional[str] = None


# Example endpoints - customize or replace these
@router.get("/example")
async def get_example():
    """Example GET endpoint."""
    logger.info("Example GET endpoint called")
    return ExampleResponse(
        success=True,
        data={"message": "This is an example endpoint"},
        message="Request successful"
    )


@router.post("/example")
async def post_example(request: ExampleRequest):
    """Example POST endpoint."""
    logger.info(f"Example POST endpoint called with: {request}")

    # Add your business logic here

    return ExampleResponse(
        success=True,
        data={"name": request.name, "value": request.value},
        message="Data processed successfully"
    )


@router.get("/example/{item_id}")
async def get_item(item_id: int):
    """Example parameterized GET endpoint."""
    logger.info(f"Fetching item: {item_id}")

    # Add your business logic here
    # Simulate item not found
    if item_id < 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item {item_id} not found"
        )

    return ExampleResponse(
        success=True,
        data={"item_id": item_id, "status": "active"},
        message="Item retrieved successfully"
    )
