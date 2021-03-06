from typing import List
from urllib import response
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import schemas, models, dependencies
from app.crud.queue import crud_queue

router = APIRouter()

@router.get("", response_model=schemas.QueueLoaded, include_in_schema=False)
@router.get("/", response_model=schemas.QueueLoaded)
async def read_queue(
        db: Session = Depends(dependencies.get_db),
        current_user: schemas.User = Depends(dependencies.get_current_user)
    ):
    return await crud_queue.get(db, current_user)

@router.get("/current", response_model=schemas.SongLoaded, include_in_schema=False)
@router.get("/current/", response_model=schemas.SongLoaded)
async def read_current(
        db: Session = Depends(dependencies.get_db),
        current_user: schemas.User = Depends(dependencies.get_current_user),
    ):
    return await crud_queue.current(db, current_user)

@router.post("/add", include_in_schema=False, response_model=schemas.Queue)
@router.post("/add/", response_model=schemas.Queue)
async def add_song_to_queue(
        song_id: int,
        db: Session = Depends(dependencies.get_db),
        current_user: schemas.User = Depends(dependencies.get_current_user),
    ):
    return await crud_queue.add(db, current_user, song_id)

@router.put("/next", response_model=schemas.SongLoaded, include_in_schema=False)
@router.put("/next/", response_model=schemas.SongLoaded)
async def next_track(
        db: Session = Depends(dependencies.get_db),
        current_user: schemas.User = Depends(dependencies.get_current_user),
    ):
    return await crud_queue.next(db, current_user)

@router.put("/prev", response_model=schemas.SongLoaded, include_in_schema=False)
@router.put("/prev/", response_model=schemas.SongLoaded)
async def previous_track(
        db: Session = Depends(dependencies.get_db),
        current_user: schemas.User = Depends(dependencies.get_current_user),
    ):
    return await crud_queue.prev(db, current_user)

@router.put("/replace", response_model=schemas.Queue, include_in_schema=False)
@router.put("/replace/", response_model=schemas.Queue)
async def replace(
        song_list: List[int],
        db: Session = Depends(dependencies.get_db),
        current_user: schemas.User = Depends(dependencies.get_current_user),
    ):
    return await crud_queue.replace(db, current_user, song_list)

@router.delete("/delete", include_in_schema=False)
@router.delete("/delete/")
async def delete_song_from_queue(
        position: int,
        db: Session = Depends(dependencies.get_db),
        current_user: schemas.User = Depends(dependencies.get_current_user),
    ):
    return await crud_queue.delete(db, current_user, position)

@router.delete("/clear", response_model=schemas.Queue, include_in_schema=False)
@router.delete("/clear/", response_model=schemas.Queue)
async def clear_queue(
        db: Session = Depends(dependencies.get_db),
        current_user: schemas.User = Depends(dependencies.get_current_user),
    ):
    return await crud_queue.clear(db, current_user)