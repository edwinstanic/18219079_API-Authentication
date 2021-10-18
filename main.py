import json
with open("menu.json", "r") as read_file:
    data = json.load(read_file)

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from typing import Optional

SECRET_KEY = "c095f58bc240512438ca166c46ddf95254cecc0e53414a934529899d0685047c"
ALGORITHM = "HS256"

users_db = {
    "asdf": {
        "username": "asdf",
        "full_name": "Admin",
        "email": "ii3160admin@gmail.com",
        "hashed_password": "$2b$12$7b4idqBRn1V6ij/LQWa7wuJeJZPlgbx.4CvGWcmTaJZ7Qr2bZCYcy",
        "disabled": False,
    }
}

# Token & User
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
app = FastAPI()

# User Authentication
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

def authenticate_user(db, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

# Token Creation
def create_access_token(data: dict):
    to_encode = data.copy()
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# Login
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.username}
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Read Hash Result
@app.get("/pass")
async def get_hash(password: str):
    return pwd_context.hash(password)

"""
Core Operation
1. Read Menu - GET
2. Update Menu - PUT
3. Add Menu  - POST
4. Delete Menu - DELETE
"""
@app.get('/menu/{item_id}')
async def read_menu(item_id: int, current_user: User = Depends(get_current_active_user)):
      for menu_item in data['menu']:
            if menu_item['id'] == item_id:
                  return menu_item

      raise HTTPException(
            status_code=404, detail=f'Item not found'
      )

@app.put('/menu/{item_id}')
async def update_menu(item_id: int, name: str, current_user: User = Depends(get_current_active_user)):
    for menu_item in data['menu']:
        if menu_item['id'] == item_id:
            menu_item['name'] = name
            read_file.close()

            with open("menu.json", "w") as write_file:
                json.dump(data, write_file, indent=4)
            
            return menu_item, {"Message": "Menu data updated"}
    
    raise HTTPException(
        status_code=404, detail=f'Item not found'
    )

@app.post('/menu')
async def add_menu(name: str, current_user: User = Depends(get_current_active_user)):
    id = 1
    if (len(data['menu']) >= 1):
        id = data['menu'][len(data['menu']) - 1]['id'] + 1
    
    new_menu = {'id': id, "name": name}
    data['menu'].append(new_menu)
    read_file.close()

    with open("menu.json", "w") as write_file:
        json.dump(data, write_file, indent=4)
        
    return (new_menu), {"Message": "Menu added"}

@app.delete('/menu/{item_id}')
async def delete_menu(item_id: int, current_user: User = Depends(get_current_active_user)):
    for menu_item in data['menu']:
        if menu_item['id'] == item_id:
            data['menu'].remove(menu_item)
            read_file.close()

            with open("menu.json", "w") as write_file:
                json.dump(data, write_file, indent=4)
            
            return {"Response": "Menu data deleted"}
    
    raise HTTPException(
        status_code=404, detail=f'Item not found'
    )