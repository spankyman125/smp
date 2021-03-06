from sqlalchemy.orm import Session, selectinload
import random
from app import models, schemas
from app.crud.base import ItemBase 
from typing import Optional, List
from sqlalchemy import desc, or_

def add_like_attr(user: models.User, albums):
    liked_songs_id = []
    liked_albums_id = []
    liked_artists_id = []

    for liked_song in user.songs:
        liked_songs_id.append(liked_song.id)
    for liked_album in user.albums:
        liked_albums_id.append(liked_album.id)
    for liked_artist in user.artists:
        liked_artists_id.append(liked_artist.id)
    
    for album in albums:
        setattr(album, "liked", True) if album.id in liked_albums_id else setattr(album, "liked", False)
        for artist in album.artists:
            setattr(artist, "liked", True) if artist.id in liked_artists_id else setattr(artist, "liked", False)
        for song in album.songs:
            setattr(song, "liked", True) if song.id in liked_songs_id else setattr(song, "liked", False)
            setattr(song.album, "liked", True) if song.album.id in liked_albums_id else setattr(song.album, "liked", False)
            for artist in song.artists:
                setattr(artist, "liked", True) if artist.id in liked_artists_id else setattr(artist, "liked", False)

class AlbumCRUD(ItemBase):
    async def get(self, db: Session, id: int, current_user: Optional[schemas.User] = None):
        album = db.query(self.model).\
            options(selectinload(self.model.songs).selectinload(models.Song.album)).\
            options(selectinload(self.model.songs).selectinload(models.Song.artists)).\
            options(selectinload(self.model.songs).selectinload(models.Song.tags)).\
            options(selectinload(self.model.artists)).\
            filter(self.model.id == id).\
            first()
        if current_user and album:
            current_db_user = db.query(models.User).filter(models.User.username == current_user.username).first()
            add_like_attr(current_db_user, [album])
        return album

    async def get_list(self, db:Session, id_list: List[int], current_user: Optional[schemas.User] = None):
        albums = db.query(models.Album).\
            filter(models.Album.id.in_(id_list)).\
            options(selectinload(self.model.songs).selectinload(models.Song.album)).\
            options(selectinload(self.model.songs).selectinload(models.Song.artists)).\
            options(selectinload(self.model.songs).selectinload(models.Song.tags)).\
            options(selectinload(self.model.artists)).\
            all()
        id_map = {t.id: t for t in albums}
        albums = [id_map[n] for n in id_list]
        if current_user:
            current_db_user = db.query(models.User).filter(models.User.username == current_user.username).first()
            add_like_attr(current_db_user, albums)
        return albums
    
    async def get_all(self, db: Session, skip: int = 0, limit: int = 100, current_user: Optional[schemas.User] = None):
        albums = db.query(self.model).\
            options(selectinload(self.model.songs).selectinload(models.Song.album)).\
            options(selectinload(self.model.songs).selectinload(models.Song.artists)).\
            options(selectinload(self.model.songs).selectinload(models.Song.tags)).\
            options(selectinload(self.model.artists)).\
            offset(skip).\
            limit(limit).\
            all()   
        if current_user:
            current_db_user = db.query(models.User).filter(models.User.username == current_user.username).first()
            add_like_attr(current_db_user, albums)
        return albums

    async def get_random(self, db: Session, limit: int = 10, current_user: Optional[schemas.User] = None):
        album_count = db.query(self.model).count()
        random_id_list = random.sample(range(1, album_count), limit)
        albums = db.query(self.model).\
            filter(models.Album.id.in_(random_id_list)).\
            options(selectinload(self.model.songs).selectinload(models.Song.album)).\
            options(selectinload(self.model.songs).selectinload(models.Song.artists)).\
            options(selectinload(self.model.songs).selectinload(models.Song.tags)).\
            options(selectinload(self.model.artists)).\
            all()   
        if current_user:
            current_db_user = db.query(models.User).filter(models.User.username == current_user.username).first()
            add_like_attr(current_db_user, albums)
        return albums
    
    async def get_recommendation(self, db: Session, id, skip: int = 0, limit: int = 5, current_user: Optional[schemas.User] = None):
        results = db.query(models.AlbumRelations).\
            filter(or_(models.AlbumRelations.id1==id,models.AlbumRelations.id2==id)).\
            order_by(models.AlbumRelations.score.desc()).\
            offset(skip).\
            limit(limit).\
            all()
        albums_id = []
        for result in results:
            if result.id1==id:
                albums_id.append(result.id2)
            else:
                albums_id.append(result.id1)

        return await self.get_list(db=db, id_list=albums_id, current_user=current_user)

    async def get_last_releases(self, db: Session, limit: int = 10, current_user: Optional[schemas.User] = None):
        albums = db.query(self.model).\
            order_by(desc(self.model.release_date)).\
            limit(limit).\
            all()   
        if current_user:
            current_db_user = db.query(models.User).filter(models.User.username == current_user.username).first()
            add_like_attr(current_db_user, albums)
        return albums

    async def like(self, db: Session, id: int, user: schemas.User):
        like = db.query(self.like_relation).get((user.id, id))
        if like:
            db.delete(like)
            db.commit()
            return False 
        else:
            like = self.like_relation(user_id=user.id, album_id=id)
            db.add(like)
            db.commit()
            db.refresh(like)
            return True 

    async def get_liked(
        self, 
        db:Session, 
        user: schemas.User, 
        current_user: Optional[schemas.User] = None
    ):
        db_user = db.query(models.User).filter(models.User.username == user.username).first()
        if current_user:
            current_db_user = db.query(models.User).filter(models.User.username == current_user.username).first()
            add_like_attr(current_db_user, db_user.albums)
        return db_user.albums

crud_album = AlbumCRUD(models.Album, models.UserAlbumLike)