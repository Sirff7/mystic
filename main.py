import psycopg2
from fastapi import FastAPI, Response, Depends, Cookie, HTTPException
from pydantic import BaseModel, Field
import re
import bcrypt
from typing import Annotated
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from generate_users import generate_users

local_db = "dbname=mystic"
_email_re = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

# DATA for seeding:
raw_users, profiles, likes = generate_users(1000)
test_salt = bcrypt.gensalt(rounds=4)
users = [
    (user_id, email, bcrypt.hashpw(password.encode(), test_salt).decode())
    for user_id, email, password in raw_users
]
# END DATA for seeding

@asynccontextmanager
async def lifespan (app: FastAPI):
    conn = psycopg2.connect(local_db)
    cur = conn.cursor()
    cur. execute(
        """
        SELECT COUNT (*)
        FROM Users;
        """
    )
    count = cur.fetchone()[0]
    if count==0:
        cur.executemany(
            """
            INSERT INTO Users (user_id, email, password_hash) 
            VALUES (%s, %s, %s)""",
            users
        )
        cur.executemany(
            """
            INSERT INTO Profiles (profile_id, display_name, bio, zodiac)
            VALUES (%s, %s, %s, %s)""",
            profiles
        )
        cur.executemany(
            """
            INSERT INTO Likes (liker, liked, likes_status)
            VALUES (%s, %s, %s)""",
            likes
        )
        conn.commit()

    cur.close()
    conn.close()
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080",],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class signup_request_body (BaseModel):
    email: str = Field (max_length= 100)
    password: str = Field (max_length= 255)

@app.post ("/users", status_code=201)
async def handle_signup(body: signup_request_body):
    is_email = re.fullmatch(_email_re, body.email)
    if is_email is None:
        raise HTTPException(status_code=400, detail="mail not valid")
    
    hashed = bcrypt.hashpw(body.password.encode(), bcrypt.gensalt()).decode()

    conn = psycopg2.connect(local_db)
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO Users (email, password_hash)
            VALUES (%s, %s)
            RETURNING user_id;
            """,
            (body.email, hashed),
        )
        user_id = cur.fetchone()
        cur.execute(
            """
            INSERT INTO Profiles (profile_id, display_name, bio, zodiac)
            VALUES ( %s, NULL, NULL, NULL)
            """,
            (user_id[0],)
        )
        conn.commit()
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        raise HTTPException(status_code=409, detail="email not unique")
    cur.close()
    conn.close()

    return {"status": "signup - ok", "user_id": user_id[0]}

class login_request_body (BaseModel):
    email: str = Field (max_length= 100)
    password: str = Field (max_length= 255)

@app.post ("/sessions", status_code=201)
async def handle_login(body: login_request_body,response: Response):
    conn = psycopg2.connect(local_db)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT user_id, password_hash FROM Users
        WHERE email=%s;
        """,
        (body.email,)
    )
    user=cur.fetchone()

    if user is None:
        raise HTTPException(status_code=401, detail="Unauthenticated")

    if bcrypt.checkpw(body.password.encode(), user[1].encode()) is False:
        raise HTTPException(status_code=401, detail="Unauthenticated")

    cur.execute(  
            """
            INSERT INTO Sessions (user_id)
            VALUES (%s)
            RETURNING token;
            """,
            (user[0],)
    )
    session = cur.fetchone()
    response.set_cookie(key="newsession", value=session[0], max_age=86400)
    
    conn.commit()
    cur.close()
    conn.close()

    return {"status": "login - ok", "user_id": user[0]}

async def require_session (newsession: Annotated[str | None, Cookie()] = None):
    token = newsession
    conn = psycopg2.connect(local_db)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT user_id FROM Sessions
        WHERE token=%s AND created_at >= NOW()- INTERVAL '24 hour';
        """,
        (token,)
    )
    session_user=cur.fetchone()
    cur.close()
    conn.close()

    if session_user is None:
        raise HTTPException(status_code=401, detail="unauthenticated")
    
    return session_user[0]

@app.get ("/me", status_code=200)
async def show_self (session_user: int = Depends(require_session)):
    conn = psycopg2.connect(local_db)
    cur = conn.cursor()
     
    cur.execute("""
        SELECT user_id, email
        FROM Users
        WHERE user_id = %s
        """,
        (session_user,))
    
    user = cur.fetchone()
    cur.close()
    conn.close()
    
    return{
        "user_id": user[0],
        "email": user[1]
    }

@app.delete ("/sessions", status_code=200)
async def handle_logout (response: Response, session_user: int = Depends(require_session)):
    conn = psycopg2.connect(local_db)
    cur = conn.cursor()  
    cur.execute("""
        DELETE FROM Sessions
        WHERE user_id = %s
        """,
        (session_user,)
        )
    conn.commit()
    cur.close()
    conn.close()
    
    response.delete_cookie(key="newsession")
    
    return{"status": "session ended"}

@app.delete ("/users", status_code=200)
async def delete_account (response: Response, session_user: int = Depends(require_session)):
    conn = psycopg2.connect(local_db)
    cur = conn.cursor()
    cur.execute("""
        DELETE FROM Users
        WHERE user_id = %s
        """,
        (session_user,)
        )
    conn.commit()
    cur.close()
    conn.close()

    response.delete_cookie(key="newsession")

    return{"status": "user and profile deleted"}

class update_profile_body (BaseModel):
    display_name: str = Field (max_length= 20)
    bio: str = Field (max_length= 1000)
    zodiac: str = Field (max_length= 20)

@app.put ("/profiles", status_code=200)
async def update_profile(body: update_profile_body, session_user: int = Depends(require_session)):
    conn = psycopg2.connect(local_db)
    cur = conn.cursor()
    try:
        cur.execute(
            """
            UPDATE Profiles
            SET display_name=%s, bio=%s, zodiac=%s 
            WHERE profile_id=%s;
            """,
            (body.display_name, body.bio, body.zodiac, session_user)
        )
        conn.commit()
    except psycopg2.errors.ForeignKeyViolation:
        conn.rollback()
        raise HTTPException(status_code=400, detail="invalid zodiac name")
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        raise HTTPException(status_code=409, detail="display_name not unique")
    cur.close()
    conn.close()
    return {"status": "profile updated"}


@app.get ("/profiles/{profile_id}", status_code=200)
async def show_profile (profile_id: int, session_user: int = Depends(require_session)):
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

@app.get ("/discoveries", status_code=200)
async def discover(session_user: int = Depends(require_session)):
    conn = psycopg2.connect(local_db)
    cur = conn.cursor()

    cur.execute("""
        SELECT zodiac 
        FROM Profiles
        WHERE profile_id = %s
        """,
        (session_user,) 
    )
    own_zodiac = cur.fetchone()

    cur.execute("""
        SELECT p.profile_id, p.display_name, p.bio, p.zodiac
        FROM Profiles p
        JOIN Matches m ON (m.zodiac_1=%s AND m.zodiac_2=p.zodiac)
        WHERE p.profile_id!= %s AND p.profile_id NOT IN (SELECT liked FROM Likes WHERE liker=%s)
        LIMIT 1;
        """,
        (own_zodiac[0], session_user, session_user))
    profile = cur.fetchone()
    cur.close()
    conn.close()

    if profile is None:
        return None
    
    return{
        "profile_id": profile[0],
        "display_name": profile[1],
        "bio": profile[2],
        "zodiac": profile[3]
    }

class likes_body (BaseModel):
    liked: int
    likes_status: int

@app.post ("/likes", status_code=201)
async def handle_likes(body: likes_body, session_user: int = Depends(require_session)):
    conn = psycopg2.connect(local_db)
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO Likes (liker, liked, likes_status)
            VALUES (%s, %s, %s);
            """,
            (session_user, body.liked, body.likes_status)
        )
    except psycopg2.errors.ForeignKeyViolation:
        conn.rollback()
        raise HTTPException(status_code=404, detail="other profile not found")
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        raise HTTPException(status_code=409, detail="like or dislike already registered") 
    conn.commit()
    cur.close()
    conn.close()

    return {"status": "like registered"}

@app.get ("/couples", status_code=200)
async def present_couples(index: int = 0,session_user: int = Depends(require_session)):
    conn = psycopg2.connect(local_db)
    cur = conn.cursor()

    cur.execute("""
                SELECT Paired_with.profile_2, Profiles.display_name, Profiles.bio, Profiles.zodiac
                FROM Paired_with
                JOIN Profiles ON Paired_with.profile_2 = Profiles.profile_id
                WHERE Paired_with.profile_1=%s

                UNION

                SELECT Paired_with.profile_1, Profiles.display_name, Profiles.bio, Profiles.zodiac
                FROM Paired_with
                JOIN Profiles ON Paired_with.profile_1 = Profiles.profile_id
                WHERE Paired_with.profile_2=%s

                LIMIT 1 OFFSET %s;
                """,
                (session_user, session_user, index)
                )
    couple = cur.fetchone()
    cur.close()
    conn.close()

    if couple is None:
        return None

    return{
        "profile_id": couple[0],
        "display_name": couple[1],
        "bio": couple[2],
        "zodiac": couple[3]
    }

