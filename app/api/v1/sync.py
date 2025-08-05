from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.services.sync_service import sync_service
from app.services.scheduler_service import scheduler_service
from datetime import datetime

router = APIRouter()

@router.post("/novels")
async def sync_novels(background_tasks: BackgroundTasks):
    """Trigger sync job cho novels"""
    try:
        print(f"🔄 Manual sync triggered at {datetime.now()}")
        result = sync_service.sync_all_novels()
        
        return {
            "success": result['success'],
            "message": "Sync job completed",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sync job failed: {str(e)}")

@router.post("/novels/background")
async def sync_novels_background(background_tasks: BackgroundTasks):
    """Trigger sync job trong background"""
    try:
        print(f"🔄 Background sync triggered at {datetime.now()}")
        
        # Add sync job to background tasks
        background_tasks.add_task(sync_service.sync_all_novels)
        
        return {
            "success": True,
            "message": "Sync job started in background",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start sync job: {str(e)}")

@router.get("/novels/status")
async def get_sync_status():
    """Lấy trạng thái sync job"""
    try:
        # Scan novels directory để xem có bao nhiêu novels
        novels = sync_service.scan_novels_directory()
        
        return {
            "novels_in_storage": len(novels),
            "last_check": datetime.now().isoformat(),
            "storage_path": str(sync_service.storage_path)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get sync status: {str(e)}")

@router.post("/novels/{novel_title}/chapters")
async def sync_novel_chapters(novel_title: str, background_tasks: BackgroundTasks):
    """Sync chỉ chapters cho một novel cụ thể"""
    try:
        print(f"🔄 Manual chapter sync triggered for novel: {novel_title}")
        
        # Tìm novel trong storage
        novels = sync_service.scan_novels_directory()
        target_novel = None
        
        for novel in novels:
            if novel.get('title') == novel_title:
                target_novel = novel
                break
        
        if not target_novel:
            raise HTTPException(status_code=404, detail=f"Novel '{novel_title}' not found in storage")
        
        # Sync chỉ chapters
        chapters = target_novel.get('chapters', [])
        result = sync_service.sync_chapters_only(novel_title, chapters)
        
        if result:
            return {
                "success": True,
                "message": f"Successfully synced {len(chapters)} chapters for novel '{novel_title}'",
                "novel_title": novel_title,
                "chapters_synced": len(chapters)
            }
        else:
            raise HTTPException(status_code=500, detail=f"Failed to sync chapters for novel '{novel_title}'")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chapter sync failed: {str(e)}")

@router.post("/scheduler/start")
async def start_scheduler():
    """Bắt đầu scheduler"""
    try:
        scheduler_service.start_scheduler()
        return {
            "success": True,
            "message": "Scheduler started successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start scheduler: {str(e)}")

@router.post("/scheduler/stop")
async def stop_scheduler():
    """Dừng scheduler"""
    try:
        scheduler_service.stop_scheduler()
        return {
            "success": True,
            "message": "Scheduler stopped successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop scheduler: {str(e)}")

@router.get("/scheduler/status")
async def get_scheduler_status():
    """Lấy trạng thái scheduler"""
    try:
        status = scheduler_service.get_scheduler_status()
        return {
            "success": True,
            "data": status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get scheduler status: {str(e)}") 