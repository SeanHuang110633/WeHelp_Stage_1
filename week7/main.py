from fastapi import FastAPI, Form, Request, Path
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import mysql.connector
from dotenv import load_dotenv
import os
import bcrypt
from fastapi import Query

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

# =============================================  week7  assignment  ======================================================
# member query processing
@app.get("/api/member")
async def get_member(request: Request, username: str = Query(None)):
    # check user state
    if not request.session.get("SIGNED-IN"):
        return {"data": "null"}
    # check username
    if not username:
        return {"data": "null"}
    # connect to DB
    conn = conn_to_DB(db_host, db_user, db_password, db_name)
    cursor = conn.cursor(dictionary=True)  

    try:
        # get the member
        cursor.execute("SELECT id, name, username FROM member WHERE username = %s", (username,))
        member = cursor.fetchone()
        if member:
            result = {
                "id": member["id"],
                "name": member["name"],
                "username": member["username"]
            }
            return {"data": result}
        else:
            return {"data": "null"}
    except mysql.connector.Error as err:
        print(f"資料庫錯誤: {err}")
        return {"data": "null"}
    finally:
        cursor.close()
        conn.close()

# update name processing
@app.patch("/api/member")
async def update_member_name(request: Request):
    # check user state
    if not request.session.get("SIGNED-IN"):
        return {"error": True}

    # get current userID from sesion
    user_id = request.session.get("user_id")
    if not user_id:
        return {"error": True}

    # get new name from request
    try:
        data = await request.json()
        new_name = data.get("name", "").strip()
    except Exception:
        return {"error": True}

    # check new name 
    if not new_name:
        return {"error": True}

    conn = conn_to_DB(db_host, db_user, db_password, db_name)
    cursor = conn.cursor()

    try:
        # update user's name
        cursor.execute("UPDATE member SET name = %s WHERE id = %s", (new_name, user_id))
        conn.commit()
        if cursor.rowcount > 0:  # check if updating succeed or not
            request.session["name"] = new_name  # update the name in session 
            return {"ok": True}
        else:
            return {"error": True}
    except mysql.connector.Error as err:
        print(f"資料庫錯誤: {err}")
        return {"error": True}
    finally:
        cursor.close()
        conn.close()

# ==========================================  week7  assignment  ======================================================

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
        cursor.execute("select member.id, member.name, message.content, message.id from member join message on member.id = message.member_id order by message.time desc")
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

    user_id = request.session.get("user_id")
    form_data = await request.form()  
    message_id = form_data.get("message_id", "").strip()

    # connect to DB
    conn = conn_to_DB(db_host, db_user, db_password, db_name)
    cursor = conn.cursor()

    # delete message 
    try:
        # check if the request is really sent by the message owner
        cursor.execute("select member_id from message where message.id = %s", (message_id,))
        member_id = cursor.fetchone()
        if not member_id or member_id[0] != user_id:
            return RedirectResponse(url="/error?message=你不能刪除這則留言", status_code=303)
        # delete message
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