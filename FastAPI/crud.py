from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# In-memory "database"
users = []
user_id_counter = 1

# Pydantic model
class User(BaseModel):
    name: str
    email: str

# Create
@app.post("/users/")
def create_user(user: User):
    global user_id_counter
    new_user = user.dict()
    new_user["id"] = user_id_counter
    users.append(new_user)
    user_id_counter += 1
    return new_user

# Get all users
@app.get("/users/")
def get_all_users():
    return users

# Read one user
@app.get("/users/{user_id}")
def read_user(user_id: int):
    for user in users:
        if user["id"] == user_id:
            return user
    raise HTTPException(status_code=404, detail="User not found")

# Update
@app.put("/users/{user_id}")
def update_user(user_id: int, updated_user: User):
    for user in users:
        if user["id"] == user_id:
            user["name"] = updated_user.name
            user["email"] = updated_user.email
            return user
    raise HTTPException(status_code=404, detail="User not found")

# Delete
@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    for i, user in enumerate(users):
        if user["id"] == user_id:
            del users[i]
            return {"detail": "User deleted"}
    raise HTTPException(status_code=404, detail="User not found")
