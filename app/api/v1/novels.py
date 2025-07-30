from fastapi import APIRouter, HTTPException, Query
from typing import List
from app.schemas.novel import NovelCreate, NovelUpdate, NovelResponse
from app.services.novel_service import NovelService

router = APIRouter()


@router.post("/", response_model=NovelResponse)
def create_novel(novel_data: NovelCreate):
    """Tạo novel mới"""
    service = NovelService()
    novel = service.create_novel(novel_data)
    return novel


@router.get("/", response_model=List[NovelResponse])
def get_novels(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: str = Query(None),
):
    """Lấy danh sách novels"""
    service = NovelService()
    
    if search:
        novels = service.search_novels(search, skip, limit)
    else:
        novels = service.get_novels(skip, limit)
    
    return novels


@router.get("/{novel_id}", response_model=NovelResponse)
def get_novel(novel_id: int):
    """Lấy thông tin novel theo ID"""
    service = NovelService()
    novel = service.get_novel(novel_id)
    
    if not novel:
        raise HTTPException(status_code=404, detail="Novel không tồn tại")
    
    # Tăng số lượt xem
    service.increment_views(novel_id)
    
    return novel


@router.put("/{novel_id}", response_model=NovelResponse)
def update_novel(novel_id: int, novel_data: NovelUpdate):
    """Cập nhật novel"""
    service = NovelService()
    novel = service.update_novel(novel_id, novel_data)
    
    if not novel:
        raise HTTPException(status_code=404, detail="Novel không tồn tại")
    
    return novel


@router.delete("/{novel_id}")
def delete_novel(novel_id: int):
    """Xóa novel"""
    service = NovelService()
    success = service.delete_novel(novel_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Novel không tồn tại")
    
    return {"message": "Novel đã được xóa thành công"} 