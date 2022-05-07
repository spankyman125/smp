from sqlalchemy.orm import Session, joinedload

from app import models, schemas
from app.crud.base import ItemBase 
from app.dependencies import add_like_attr
from typing import Optional, List

class AlbumCRUD(ItemBase):
    def get(self, db: Session, id: int, current_user: Optional[schemas.User] = None):
        album = db.query(self.model).\
            options(joinedload(self.model.songs)).\
            options(joinedload(self.model.artists)).\
            filter(self.model.id == id).\
            first()
        if current_user:
            current_db_user = db.query(models.User).filter(models.User.username == current_user.username).first()
            add_like_attr(current_db_user, [album], "albums")
            add_like_attr(current_db_user, album.songs, "songs")
            add_like_attr(current_db_user, album.artists, "artists")
        return album

    def get_list(self, db:Session, id_list: List[int], current_user: Optional[schemas.User] = None):
        albums = db.query(models.Album).\
            filter(models.Album.id.in_(id_list)).\
            all()
            # options(joinedload(self.model.songs)).\
            # options(joinedload(self.model.artists)).\
        id_map = {t.id: t for t in albums}
        albums = [id_map[n] for n in id_list]
        if current_user:
            current_db_user = db.query(models.User).filter(models.User.username == current_user.username).first()
            for i in range(len(albums)):
                add_like_attr(current_db_user, [albums[i]], "albums")
                # add_like_attr(current_db_user, albums[i].songs, "songs")
                # add_like_attr(current_db_user, albums[i].artists, "artists")
        return albums
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100, current_user: Optional[schemas.User] = None):
        albums = db.query(self.model).\
            options(joinedload(self.model.songs)).\
            options(joinedload(self.model.artists)).\
            offset(skip).\
            limit(limit).\
            all()   
        if current_user:
            current_db_user = db.query(models.User).filter(models.User.username == current_user.username).first()
            for i in range(len(albums)):
                add_like_attr(current_db_user, [albums[i]], "albums")
                add_like_attr(current_db_user, albums[i].songs, "songs")
                add_like_attr(current_db_user, albums[i].artists, "artists")
        return albums


    def like(self, db: Session, id: int, user: schemas.User):
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

    def get_liked(
        self, 
        db:Session, 
        user: schemas.User, 
        current_user: Optional[schemas.User] = None
    ):
        db_user = db.query(models.User).filter(models.User.username == user.username).first()
        if current_user:
            current_db_user = db.query(models.User).filter(models.User.username == current_user.username).first()
            add_like_attr(current_db_user, db_user.albums, "albums")
        return db_user.albums

crud_album = AlbumCRUD(models.Album, models.UserAlbumLike)