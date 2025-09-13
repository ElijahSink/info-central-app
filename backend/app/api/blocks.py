from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, field_serializer
from datetime import datetime

from ..core.database import get_db
from ..services.block_service import BlockService
from ..models.block import Block, BlockVersion


router = APIRouter(prefix="/blocks", tags=["blocks"])
block_service = BlockService()


# Pydantic models for requests/responses
class CreateBlockRequest(BaseModel):
    user_prompt: str
    title: Optional[str] = None
    refresh_interval: int = 3600


class UpdateBlockRequest(BaseModel):
    user_prompt: str


class LayoutUpdateRequest(BaseModel):
    layout_data: Dict[str, Any]


class BlockResponse(BaseModel):
    id: int
    user_prompt: str
    title: str
    current_version: int
    refresh_interval: int
    layout_data: Dict[str, Any]
    status: str
    created_at: datetime
    updated_at: datetime

    @field_serializer('created_at', 'updated_at')
    def serialize_datetime(self, value: datetime) -> str:
        return value.isoformat()

    class Config:
        from_attributes = True


class BlockVersionResponse(BaseModel):
    id: int
    version: int
    frontend_code: str
    ai_explanation: str
    created_at: datetime
    status: str

    @field_serializer('created_at')
    def serialize_datetime(self, value: datetime) -> str:
        return value.isoformat()

    class Config:
        from_attributes = True


@router.get("/", response_model=List[BlockResponse])
async def get_blocks(db: Session = Depends(get_db)):
    """Get all active blocks."""
    blocks = block_service.get_blocks(db)
    return [BlockResponse.model_validate(block) for block in blocks]


@router.get("/{block_id}", response_model=BlockResponse)
async def get_block(block_id: int, db: Session = Depends(get_db)):
    """Get a specific block."""
    block = block_service.get_block(db, block_id)
    if not block:
        raise HTTPException(status_code=404, detail="Block not found")
    return BlockResponse.model_validate(block)


@router.post("/", response_model=BlockResponse)
async def create_block(
    request: CreateBlockRequest, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Create a new block with AI-generated code."""
    try:
        block = await block_service.create_block(
            db=db,
            user_prompt=request.user_prompt,
            title=request.title,
            refresh_interval=request.refresh_interval
        )
        
        # Schedule background refresh
        background_tasks.add_task(
            schedule_block_refresh, 
            block.id, 
            request.refresh_interval
        )
        
        return BlockResponse.model_validate(block)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{block_id}", response_model=BlockResponse)
async def update_block(
    block_id: int,
    request: UpdateBlockRequest,
    db: Session = Depends(get_db)
):
    """Update a block with user iteration."""
    try:
        block = await block_service.update_block(
            db=db,
            block_id=block_id,
            user_prompt=request.user_prompt
        )
        return BlockResponse.model_validate(block)
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{block_id}")
async def delete_block(block_id: int, db: Session = Depends(get_db)):
    """Delete a block."""
    success = block_service.delete_block(db, block_id)
    if not success:
        raise HTTPException(status_code=404, detail="Block not found")
    return {"message": "Block deleted successfully"}


@router.post("/{block_id}/refresh")
async def refresh_block(block_id: int, db: Session = Depends(get_db)):
    """Manually refresh block data."""
    try:
        data = await block_service.refresh_block_data(db, block_id)
        return {"data": data, "refreshed_at": str(datetime.utcnow())}
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{block_id}/heal")
async def heal_block(block_id: int, db: Session = Depends(get_db)):
    """Attempt to heal a failed block."""
    try:
        block = await block_service.heal_block(db, block_id)
        return BlockResponse.model_validate(block)
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{block_id}/layout")
async def update_block_layout(
    block_id: int,
    request: LayoutUpdateRequest,
    db: Session = Depends(get_db)
):
    """Update block layout information."""
    success = block_service.update_block_layout(db, block_id, request.layout_data)
    if not success:
        raise HTTPException(status_code=404, detail="Block not found")
    return {"message": "Layout updated successfully"}


@router.get("/{block_id}/versions", response_model=List[BlockVersionResponse])
async def get_block_versions(block_id: int, db: Session = Depends(get_db)):
    """Get all versions of a block."""
    block = block_service.get_block(db, block_id)
    if not block:
        raise HTTPException(status_code=404, detail="Block not found")
    
    versions = db.query(BlockVersion).filter(
        BlockVersion.block_id == block_id
    ).order_by(BlockVersion.version.desc()).all()
    
    return [BlockVersionResponse.model_validate(version) for version in versions]


@router.get("/{block_id}/data")
async def get_block_data(block_id: int, db: Session = Depends(get_db)):
    """Get cached data for a block."""
    from ..models.block import BlockData
    from datetime import datetime
    
    # Get most recent cached data
    cached_data = db.query(BlockData).filter(
        BlockData.block_id == block_id
    ).order_by(BlockData.fetched_at.desc()).first()
    
    if not cached_data:
        # No cached data, refresh it
        data = await block_service.refresh_block_data(db, block_id)
        return {"data": data, "cached": False, "refreshed_at": str(datetime.utcnow())}
    
    # Check if data is still valid
    if cached_data.expires_at and datetime.utcnow() > cached_data.expires_at:
        # Data expired, refresh it
        data = await block_service.refresh_block_data(db, block_id)
        return {"data": data, "cached": False, "refreshed_at": str(datetime.utcnow())}
    
    return {
        "data": cached_data.data, 
        "cached": True, 
        "fetched_at": str(cached_data.fetched_at)
    }


# Background task helpers
async def schedule_block_refresh(block_id: int, interval: int):
    """Background task to refresh block data periodically."""
    import asyncio
    from datetime import datetime
    
    # This is a simplified version - in production you'd want a proper scheduler
    await asyncio.sleep(interval)
    
    # Could implement actual refresh logic here
    # For now, this is just a placeholder