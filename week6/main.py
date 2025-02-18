from fastapi import FastAPI, Form, Request, Path
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import mysql.connector
from dotenv import load_dotenv
import os
import bcrypt

# MySQL connection data 
load_dotenv()  
db_user = os.getenv("MYSQL_USER")
db_password = os.getenv("MYSQL_PASSWORD")
db_host = "localhost"
db_name = "website"

app = FastAPI()
# Set up SessionMiddleware
secret_key = os.getenv("secret_key")
app.add_middleware(SessionMiddleware, secret_key=secret_key) 

# Set template directory
templates = Jinja2Templates(directory="templates")

# Homepage processing
@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

# Sign-up processing
@app.post("/signup")
async def signup(request: Request):
    form_data = await request.form()
    name = form_data.get("name", "").strip()
    username = form_data.get("username", "").strip()
    password = form_data.get("password", "").strip()

    if not username:
        return RedirectResponse(url="/error?message=你未輸入姓名", status_code=303)

    # connect to DB
    conn = conn_to_DB(db_host, db_user, db_password, db_name)
    cursor = conn.cursor()

    # check if the username has been used
    try:
        cursor.execute("SELECT username FROM member WHERE username = %s", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            return RedirectResponse(url="/error?message=帳號已被使用", status_code=303)

        # username has not been used -> Insert user
        hashed_pwd = hash_password(password)
        cursor.execute("INSERT INTO member (name, username, password) VALUES (%s,%s,%s)", (name, username, hashed_pwd))
        conn.commit()
    except mysql.connector.Error as err:
        print(f"資料庫錯誤: {err}")
        return RedirectResponse(url="/error?message=資料庫錯誤", status_code=303)
    finally:
        # release the connection resources
        cursor.close()
        conn.close()
    
    # signup success and redirect to homepage
    return RedirectResponse(url="/", status_code=303)

# Sign-in processing
@app.post("/signin")
async def signin(request: Request):
    form_data = await request.form()  
    username = form_data.get("username", "").strip()
    password = form_data.get("password", "").strip()

    if not username or not password: 
        # If username or password is not filled, redirect to the error page
        return RedirectResponse(url="/error?message=請輸入帳號密碼", status_code=303)

    # connect to DB
    conn = conn_to_DB(db_host, db_user, db_password, db_name)
    cursor = conn.cursor()

    # check username and pwd
    try:
        cursor.execute("SELECT id, name, username, password FROM member WHERE username = %s " , (username,))
        user = cursor.fetchone()

        # check username
        if user is None:
            return RedirectResponse(url="/error?message=帳號或密碼輸入錯誤", status_code=303)

        # check pwd  
        hashed_password = user[3]
        if bcrypt.checkpw(password.encode(), hashed_password.encode()):
            request.session["SIGNED-IN"] = True
            request.session["user_id"] = user[0]
            request.session["name"] = user[1]
            request.session["username"] = user[2]
            # signin success and redirect to member page
            return RedirectResponse(url="/member", status_code=303)
        else:
            return RedirectResponse(url="/error?message=帳號或密碼輸入錯誤", status_code=303)
    except mysql.connector.Error as err:
        print(f"資料庫錯誤: {err}")
        return RedirectResponse(url="/error?message=Database Error", status_code=303)
    finally:
        cursor.close()
        conn.close()

# Sign-out processing
@app.get("/signout")
async def signout(request: Request):
    request.session.clear()  
    return RedirectResponse(url="/", status_code=303)

# Member page processing
@app.get("/member")
async def member(request: Request):
    # check user state
    if not request.session.get("SIGNED-IN"):
        return RedirectResponse(url="/", status_code=303)

    # get user data from session 
    name = request.session.get("name", None)
    user_id = request.session.get("user_id", None)

    # connect to DB
    conn = conn_to_DB(db_host, db_user, db_password, db_name)
    cursor = conn.cursor()

    # get all the messages
    try:
        cursor.execute("select member.id, member.name, message.content, message.id from member join message on member.id = message.member_id")
        messages = cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"資料庫錯誤: {err}")
        return RedirectResponse(url="/error?message=Database Error", status_code=303)
    finally:
        cursor.close()
        conn.close() 
    # pass data to member page
    return templates.TemplateResponse(
        "member.html",
        {
            "request": request,
            "name": name,
            "user_id":user_id,
            "messages": messages
        }
    )

# Error page processing
@app.get("/error")
async def error(request: Request, message: str):
    return templates.TemplateResponse("error.html", {"request": request, "message": message})


@app.post("/createMessage")
async def createmessage(request: Request):
    # check user state
    if not request.session.get("SIGNED-IN"):
        return RedirectResponse(url="/", status_code=303)

    form_data = await request.form()  
    content = form_data.get("content", "").strip()
    
    # check is message is empty
    if not content:
        return RedirectResponse(url="/member", status_code=303)

    # connect to DB
    conn = conn_to_DB(db_host, db_user, db_password, db_name)
    cursor = conn.cursor()

    # insert message content
    user_id = request.session.get("user_id", None)
    try:
        cursor.execute("INSERT INTO message (member_id, content) VALUES (%s,%s)", (user_id, content))
        conn.commit()
        return RedirectResponse(url="/member", status_code=303)
    except mysql.connector.Error as err:
        print(f"資料庫錯誤: {err}")
        return RedirectResponse(url="/error?message=Database Error", status_code=303)
    finally:
        cursor.close()
        conn.close()
    # create message success and redirect to member page
    return RedirectResponse(url="/member", status_code=303)


@app.post("/deleteMessage")
async def deletemessage(request: Request):
    # check user state
    if not request.session.get("SIGNED-IN"):
        return RedirectResponse(url="/", status_code=303)

    form_data = await request.form()  
    message_id = form_data.get("message_id", "").strip()

    # connect to DB
    conn = conn_to_DB(db_host, db_user, db_password, db_name)
    cursor = conn.cursor()

    # delete message 
    try:
        cursor.execute("DELETE FROM message WHERE id = %s", (message_id,))
        conn.commit()
    except mysql.connector.Error as err:
        print(f"資料庫錯誤: {err}")
        return RedirectResponse(url="/error?message=Database Error", status_code=303)
    finally:
        cursor.close()
        conn.close()
    # delete message success and redirect to member page
    return RedirectResponse(url="/member", status_code=303)

# ====================================================================================================

# founction for connect to DB
def conn_to_DB(db_host : str, db_user : str, db_pwd : str, db_Name : str):
    return mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_pwd,
        database=db_Name
    )
    
# founction for hashing the password
def hash_password(plain_password : str) :
    salt = bcrypt.gensalt()  
    hashed = bcrypt.hashpw(plain_password.encode(), salt)  
    return hashed.decode() 
