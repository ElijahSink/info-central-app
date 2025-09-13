from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from ..models.block import Block, BlockVersion, BlockData, ExecutionLog
from .ai_service import AIService
from .execution_service import ExecutionService
import json
from datetime import datetime, timedelta


class BlockService:
    def __init__(self):
        self.ai_service = AIService()
        self.execution_service = ExecutionService()
    
    async def create_block(
        self, 
        db: Session, 
        user_prompt: str,
        title: Optional[str] = None,
        refresh_interval: int = 3600
    ) -> Block:
        """Create a new block with AI-generated code."""
        
        # Generate code using AI
        generated_code = await self.ai_service.generate_block_code(user_prompt)
        
        # Create block record
        block = Block(
            user_prompt=user_prompt,
            title=title or self._generate_title(user_prompt),
            refresh_interval=refresh_interval,
            layout_data={"x": 0, "y": 0, "w": 6, "h": 4}  # Default layout
        )
        db.add(block)
        db.flush()  # Get the block ID
        
        # Create first version
        version = BlockVersion(
            block_id=block.id,
            version=1,
            backend_code=generated_code["backend_code"],
            frontend_code=generated_code["frontend_code"],
            ai_explanation=generated_code["explanation"]
        )
        db.add(version)
        
        # Test the generated code
        try:
            await self.execution_service.execute_block(block.id, 1, generated_code["backend_code"])
            block.status = "active"
        except Exception as e:
            block.status = "error"
            # Log the error
            error_log = ExecutionLog(
                block_id=block.id,
                version=1,
                execution_type="fetch",
                success=False,
                error_message=str(e)
            )
            db.add(error_log)
        
        db.commit()
        db.refresh(block)
        return block
    
    async def update_block(
        self, 
        db: Session, 
        block_id: int, 
        user_prompt: str
    ) -> Block:
        """Update a block with a new version based on user iteration."""
        
        block = db.query(Block).filter(Block.id == block_id).first()
        if not block:
            raise ValueError(f"Block {block_id} not found")
        
        # Get context from previous versions
        previous_version = db.query(BlockVersion).filter(
            BlockVersion.block_id == block_id,
            BlockVersion.version == block.current_version
        ).first()
        
        context = {
            "original_prompt": block.user_prompt,
            "previous_code": previous_version.backend_code if previous_version else None,
            "iteration": user_prompt
        }
        
        # Generate new code
        generated_code = await self.ai_service.generate_block_code(user_prompt, context)
        
        # Create new version
        new_version = block.current_version + 1
        version = BlockVersion(
            block_id=block.id,
            version=new_version,
            backend_code=generated_code["backend_code"],
            frontend_code=generated_code["frontend_code"],
            ai_explanation=generated_code["explanation"]
        )
        db.add(version)
        
        # Test the new version
        try:
            await self.execution_service.execute_block(block.id, new_version, generated_code["backend_code"])
            block.current_version = new_version
            block.status = "active"
        except Exception as e:
            block.status = "error"
            # Log the error
            error_log = ExecutionLog(
                block_id=block.id,
                version=new_version,
                execution_type="fetch",
                success=False,
                error_message=str(e)
            )
            db.add(error_log)
        
        block.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(block)
        return block
    
    async def heal_block(self, db: Session, block_id: int) -> Block:
        """Attempt to heal a failed block using AI."""
        
        block = db.query(Block).filter(Block.id == block_id).first()
        if not block:
            raise ValueError(f"Block {block_id} not found")
        
        # Get the current version and latest error
        current_version = db.query(BlockVersion).filter(
            BlockVersion.block_id == block_id,
            BlockVersion.version == block.current_version
        ).first()
        
        latest_error = db.query(ExecutionLog).filter(
            ExecutionLog.block_id == block_id,
            ExecutionLog.success == False
        ).order_by(ExecutionLog.created_at.desc()).first()
        
        if not current_version or not latest_error:
            raise ValueError("Cannot heal block: missing version or error information")
        
        # Attempt healing
        try:
            healed_code = await self.ai_service.heal_block(
                original_prompt=block.user_prompt,
                error_message=latest_error.error_message,
                failed_code=current_version.backend_code
            )
            
            # Create healed version
            new_version = block.current_version + 1
            version = BlockVersion(
                block_id=block.id,
                version=new_version,
                backend_code=healed_code["backend_code"],
                frontend_code=healed_code["frontend_code"],
                ai_explanation=f"Auto-healed: {healed_code['explanation']}"
            )
            db.add(version)
            
            # Test the healed version
            await self.execution_service.execute_block(block.id, new_version, healed_code["backend_code"])
            
            block.current_version = new_version
            block.status = "active"
            block.updated_at = datetime.utcnow()
            
            # Log successful healing
            heal_log = ExecutionLog(
                block_id=block.id,
                version=new_version,
                execution_type="heal",
                success=True
            )
            db.add(heal_log)
            
        except Exception as e:
            # Log failed healing attempt
            heal_log = ExecutionLog(
                block_id=block.id,
                version=block.current_version,
                execution_type="heal",
                success=False,
                error_message=str(e)
            )
            db.add(heal_log)
        
        db.commit()
        db.refresh(block)
        return block
    
    async def refresh_block_data(self, db: Session, block_id: int) -> Dict[str, Any]:
        """Refresh data for a block."""
        
        block = db.query(Block).filter(Block.id == block_id).first()
        if not block:
            raise ValueError(f"Block {block_id} not found")
        
        current_version = db.query(BlockVersion).filter(
            BlockVersion.block_id == block_id,
            BlockVersion.version == block.current_version
        ).first()
        
        if not current_version:
            raise ValueError(f"No version found for block {block_id}")
        
        try:
            # Execute the block to get fresh data
            data = await self.execution_service.execute_block(
                block.id, 
                block.current_version, 
                current_version.backend_code
            )
            
            # Cache the data
            block_data = BlockData(
                block_id=block.id,
                data=data,
                expires_at=datetime.utcnow() + timedelta(seconds=block.refresh_interval)
            )
            db.add(block_data)
            
            # Log successful execution
            exec_log = ExecutionLog(
                block_id=block.id,
                version=block.current_version,
                execution_type="fetch",
                success=True
            )
            db.add(exec_log)
            
            db.commit()
            return data
            
        except Exception as e:
            # Log execution error
            exec_log = ExecutionLog(
                block_id=block.id,
                version=block.current_version,
                execution_type="fetch",
                success=False,
                error_message=str(e)
            )
            db.add(exec_log)
            db.commit()
            
            # Attempt auto-healing if this is the first recent failure
            recent_errors = db.query(ExecutionLog).filter(
                ExecutionLog.block_id == block_id,
                ExecutionLog.success == False,
                ExecutionLog.created_at > datetime.utcnow() - timedelta(hours=1)
            ).count()
            
            if recent_errors <= 1:  # First recent failure, try healing
                try:
                    await self.heal_block(db, block_id)
                    # Retry after healing
                    return await self.refresh_block_data(db, block_id)
                except:
                    pass  # Healing failed, will return error
            
            raise e
    
    def get_blocks(self, db: Session) -> List[Block]:
        """Get all active blocks."""
        return db.query(Block).filter(Block.status != "deleted").all()
    
    def get_block(self, db: Session, block_id: int) -> Optional[Block]:
        """Get a specific block."""
        return db.query(Block).filter(Block.id == block_id).first()
    
    def delete_block(self, db: Session, block_id: int) -> bool:
        """Soft delete a block."""
        block = db.query(Block).filter(Block.id == block_id).first()
        if block:
            block.status = "deleted"
            db.commit()
            return True
        return False
    
    def update_block_layout(self, db: Session, block_id: int, layout_data: Dict[str, Any]) -> bool:
        """Update block layout information."""
        block = db.query(Block).filter(Block.id == block_id).first()
        if block:
            block.layout_data = layout_data
            block.updated_at = datetime.utcnow()
            db.commit()
            return True
        return False
    
    def _generate_title(self, prompt: str) -> str:
        """Generate a simple title from the user prompt."""
        # Simple title generation - take first few words
        words = prompt.strip().split()[:4]
        return " ".join(words).title()