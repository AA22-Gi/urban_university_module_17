from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.backend.db_depends import get_db
from typing import Annotated

from app.models import *
from app.schemas import CreateUser, UpdateUser
from sqlalchemy import insert, select, update, delete

from slugify import slugify

router = APIRouter(prefix='/user', tags=['user'])


@router.get('/')
async def all_users(db: Annotated[Session, Depends(get_db)]):
    users = db.scalars(select(User)).all()
    return users


@router.get('/user_id')
async def user_by_id(user_id: int, db: Annotated[Session, Depends(get_db)]):
    user_ = db.scalars(select(User).where(User.id == user_id))
    if user_ is None:
        raise HTTPException(status_code=404, detail="User  was not found")
    return user_


@router.post('/create')
async def create_user(create_new_user: CreateUser, db: Annotated[Session, Depends(get_db)]):
    # Проверка на существование пользователя
    result = db.execute(select(User).where(User.username == create_new_user.username)).fetchone()
    if result is not None:
        raise HTTPException(status_code=400, detail="User  with this username already exists")

    # Создание нового пользователя
    db.execute(insert(User).values(
        username=create_new_user.username,
        firstname=create_new_user.firstname,
        lastname=create_new_user.lastname,
        age=create_new_user.age,
        slug=slugify(create_new_user.username)
    ))
    db.commit()
    return {'status_code': status.HTTP_201_CREATED, 'transaction': 'Successful'}


@router.put('/update/{user_id}')
async def update_user(user_id: int, updated_user: UpdateUser , db: Annotated[Session, Depends(get_db)]):
    # Проверка на существование пользователя
    result = db.execute(select(User).where(User.id == user_id)).fetchone()
    if result is None:
        raise HTTPException(status_code=404, detail="User  not found")

    # Обновление данных пользователя
    db.execute(update(User).where(User.id == user_id).values(
        username=updated_user.username,
        firstname=updated_user.firstname,
        lastname=updated_user.lastname,
        age=updated_user.age,
        slug=slugify(updated_user.username)
    ))
    db.commit()
    return {'status_code': status.HTTP_200_OK, 'transaction': 'User  updated successfully'}


@router.delete('/delete')
async def delete_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    # Проверка на существование пользователя
    result = db.execute(select(User).where(User.id == user_id)).fetchone()
    if result is None:
        raise HTTPException(status_code=404, detail="User  not found")

    # Удаление пользователя
    db.execute(delete(User).where(User.id == user_id))
    db.commit()
    return {'status_code': status.HTTP_200_OK, 'transaction': 'User  deleted successfully'}
