import psycopg2
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import re

app = FastAPI()
local_db = "dbname=learning"
_email_re = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

# @app.get("/health")
# async def read_root():
#     return {"Hello": "World"}

class signup_request_body (BaseModel):
    email: str
    password: str

@app.post ("/users", status_code=201)
async def handle_signup(body: signup_request_body):
    is_email = re.fullmatch(_email_re, body.email)
    if is_email is None:
        raise HTTPException(status_code=400, detail="mail not valid")
    
    conn = psycopg2.connect(local_db)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO Users (email, password)
        VALUES (%s, %s)
        RETURNING user_id;
        """,
        (body.email, body.password),
    )
    user_id = cur.fetchone()[0]
    cur.execute(
        """
        INSERT INTO Profiles (display_name, bio, user_id, zodiac)
        VALUES (NULL, NULL, %s, NULL)
        RETURNING profile_id;
        """,
        (user_id,)
    )
    profile_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()

    return {"status": "signup - ok", "user_id": user_id, "profile_id": profile_id}

class login_request_body (BaseModel):
    email: str
    password: str

@app.get ("/users", status_code=200)
async def handle_login(body: login_request_body):
    conn = psycopg2.connect(local_db)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT user_id FROM Users
        WHERE email=%s AND password=%s;
        """,
        (body.email, body.password)
    )
    user=cur.fetchone()
    cur.close()
    conn.close()
    
    if user is None:
        raise HTTPException(status_code=401, detail="unauthenticated")

    return {"status": "login - ok", "user_id": user[0]}

class update_profile_body (BaseModel):
    display_name: str
    bio: str
    zodiac: str

@app.put ("/profiles/{profile_id}", status_code=200)
async def update_profile(profile_id: int, body: update_profile_body):
    conn = psycopg2.connect(local_db)
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE Profiles
        SET display_name=%s, bio=%s, zodiac=%s 
        WHERE profile_id=%s;
        """,
        (body.display_name, body.bio, body.zodiac, profile_id)
    )
    conn.commit()
    cur.close()
    conn.close()
   
    return {"status": "profile updated"}

@app.get ("/profiles/{profile_id}", status_code=200)
async def show_profile(profile_id:int):
    conn = psycopg2.connect(local_db)
    cur = conn.cursor()

    cur.execute("""
        SELECT profile_id, display_name, bio, zodiac
        FROM Profiles
        WHERE profile_id = %s
        """,
        (profile_id,))
    
    profile = cur.fetchone()
    cur.close()
    conn.close()

    if profile is None:
        raise HTTPException(status_code=404, detail="profile not found")
    
    return{
        "profile_id": profile[0],
        "display_name": profile[1],
        "bio": profile[2],
        "zodiac": profile[3]
    }

@app.delete ("/users/{user_id}", status_code=200)
async def delete_account (user_id:int):
    conn = psycopg2.connect(local_db)
    cur = conn.cursor()
    cur.execute("""
        DELETE FROM Users
        WHERE user_id = %s
        """,
        (user_id,)
        )
    conn.commit()
    rows_affected = cur.rowcount
    cur.close()
    conn.close()
    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="user not found")
    return{"status": "user and profile deleted"}

@app.get ("/discoveries/{profile_id}", status_code=200)
async def discover(profile_id:int):
    conn = psycopg2.connect(local_db)
    cur = conn.cursor()

    cur.execute("""
        SELECT zodiac 
        FROM Profiles
        WHERE profile_id = %s
        """,
        (profile_id,) 
    )
    result = cur.fetchone()
    if result is None:
        raise HTTPException(status_code=404, detail="profile not found")
    current_zodiac = result[0]

    cur.execute("""
        SELECT p.profile_id, p.display_name, p.bio, p.zodiac
        FROM Profiles p
        JOIN Matches m ON (m.zodiac_1=%s AND m.zodiac_2=p.zodiac)
        WHERE p.profile_id!= %s AND p.profile_id NOT IN (SELECT liked FROM Likes WHERE liker=%s)
        LIMIT 1;
        """,
        (current_zodiac, profile_id, profile_id))
    profile = cur.fetchone()
    cur.close()
    conn.close()

    if profile is None:
        return{"status": "no more compatible profiles available"}
    return{
        "profile_id": profile[0],
        "display_name": profile[1],
        "bio": profile[2],
        "zodiac": profile[3]
    }

class likes_body (BaseModel):
    liker: int
    liked: int
    likes_status: int

@app.post ("/likes", status_code=201)
async def handle_likes(body: likes_body):
    conn = psycopg2.connect(local_db)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO Likes (liker, liked, likes_status)
        VALUES (%s, %s, %s)
        RETURNING likes_status;
        """,
        (body.liker, body.liked, body.likes_status)
    )
    liker_likes = cur.fetchone()[0]

    if liker_likes==1:
        cur.execute(
            """
            SELECT l.likes_status
            FROM Likes l
            WHERE l.liker=%s AND l.liked=%s;
            """,
            (body.liked, body.liker),
        )
        liked_likes = cur.fetchone()
        if liked_likes is not None and liked_likes[0]==1:
            cur.execute(
            """
            INSERT INTO Paired_with (profile_1, profile_2)
            VALUES (%s, %s);
            """,
            (body.liker, body.liked),
            )

    conn.commit()
    cur.close()
    conn.close()

    return {"status": "like registered"}

@app.get ("/couples/{profile_id}", status_code=200)
async def present_couples(profile_id:int):
    conn = psycopg2.connect(local_db)
    cur = conn.cursor()

    cur.execute("""
                SELECT *
                FROM Paired_with
                WHERE profile_1=%s OR profile_2=%s
                """,
                (profile_id, profile_id)
                )
    couple = cur.fetchall()
    cur.close()
    conn.close()

    if couple==[]:
        return{"status": "no mutual likes yet"}
    return{
        "mutual likes": couple,
        }


# def main():
#     print("Hello from mystic!")
