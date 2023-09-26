import sys

from fastapi import status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from exception import http_exception
from routers.auth import get_current_user, get_password_hash, verify_password

sys.path.append("..")

from fastapi import APIRouter, Depends, Form, Request

import models
from database import SessionLocal, engine

router_users = APIRouter(
    tags=["Users"],
    prefix="/user",
    responses={401: {"user": "Not authorized"}}
)

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

@router_users.get("/all_users")
async def get_all_users(db: Session = Depends(get_db)):
    return db.query(models.Users).all()


@router_users.get("/")
async def user_by_query(user_id: int, db: Session = Depends(get_db)):
    user_model = db.query(models.Users).filter(models.Users.id == user_id).first()
    if user_model is not None:
        return user_model
    raise http_exception()


@router_users.get("/edit-password", response_class=HTMLResponse)
async def edit_user_view(request: Request):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("edit-user-password.html", {"request": request, "user": user})


@router_users.post("/edit-password", response_class=HTMLResponse)
async def user_password_change(request: Request, db: Session = Depends(get_db), username: str = Form(...),
                                password: str = Form(...), password2: str = Form(...)):

    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    user_data = db.query(models.Users).filter(models.Users.username == username).first()
    msg = "Invalid username pr password"
    if user_data is not None:
        if username == user_data.username and verify_password(password, user_data.hashed_password):
            user_data.hashed_password = get_password_hash(password2)
            db.add(user_data)
            db.commit()
            msg = "Password Updated!"

    return templates.TemplateResponse("edit-user-password.html", {"request": request, "user": user, "msg": msg})



# @router_users.get("/")
# async def user_by_query(user_id: int, db: Session = Depends(get_db)):
#     user_model = db.query(models.Users).filter(models.Users.id == user_id).first()
#     if user_model is not None:
#         return user_model
#     raise http_exception()


# @router_users.put("/password")
# async def user_password_change(user_verification: UserVerification, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
#     if user is None:
#         raise get_user_exception()
#     user_model = db.query(models.Users).filter(models.Users.id == user.get('id')).first()
#     if user_model is not None:
#         if user_verification.username == user_model.username and verify_password(user_verification.password, user_model.hashed_password):
#             user_model.hashed_password = get_password_hash(user_verification.new_password)
#             db.add(user_model)
#             db.commit()
#             return "successful"
#     return 'Error'


# @router_users.delete("/delete_users")
# async def delete_user(user_id: int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
#     if user is None:
#         raise get_user_exception()
#     user_model = db.query(models.Users).filter(models.Users.id == user.get("id")).first()
#     if user_model is None:
#         return "Invalid user or request"
#     db.query(models.Users).filter(models.Users.id == user.get("id")).delete()
#     db.commit()
#     return "Delete Successful"


# @router_users.get("/{user_id}")
# async def user_by_path(user_id: int, db: Session = Depends(get_db)):
#     user_model = db.query(models.Users).filter(models.Users.id == user_id).first()
#     if user_model is not None:
#         return user_model
#     raise http_exception()
