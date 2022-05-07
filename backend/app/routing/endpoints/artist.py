from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models
from app import schemas
from app import dependencies
from .endpoint_item import artist_endpoint

router = APIRouter()

@router.get("/{id}", response_model=schemas.ArtistLoaded)
def read_artist(
        id: int, 
        db: Session = Depends(dependencies.get_db),
        current_user: schemas.UserReturn = Depends(dependencies.get_current_user_optional)
    ):
    return artist_endpoint.read(db, id, current_user)

@router.put("/{id}/like")
def like_artist(
        id: int, 
        db: Session = Depends(dependencies.get_db), 
        current_user: schemas.UserReturn = Depends(dependencies.get_current_user)
    ):
    return artist_endpoint.like(db, id, current_user)

@router.get("/", response_model=List[schemas.ArtistLoaded])
def read_artists(
        skip: int = 0, 
        limit: int = 100, 
        db: Session = Depends(dependencies.get_db),
        current_user: schemas.UserReturn = Depends(dependencies.get_current_user_optional)
    ):
    return artist_endpoint.read_all(db, skip, limit, current_user)
