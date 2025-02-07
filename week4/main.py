from fastapi import FastAPI, Form, Request, Path
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()
# 設定 SessionMiddleware
app.add_middleware(SessionMiddleware, secret_key="wehelpWeek4") 

# 設定模板資料夾
templates = Jinja2Templates(directory="templates")


# 訪問首頁
@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

# 登入處理 
@app.post("/signin")
async def signin(request: Request):
    form_data = await request.form()  # 取得所有表單數據
    account = form_data.get("account", "").strip()
    password = form_data.get("password", "").strip()
    if not account or not password: 
         # 未輸入帳號or密碼，轉跳錯誤頁
        return RedirectResponse(url="/error?message=請輸入帳號及密碼", status_code=303)

    # 驗證帳號密碼是否為正確(test、test)，正確則轉跳會員頁
    if account == "test" and password == "test":
        request.session["SIGNED-IN"] = True  # 設定使用者為登入狀態
        return RedirectResponse(url="/member", status_code=303)
    else:
        # 帳號or密碼錯誤，轉跳錯誤頁
        return RedirectResponse(url="/error?message=帳號、或密碼輸入錯誤", status_code=303)

# 登出處理
@app.get("/signout")
async def signout(request: Request):
    request.session["SIGNED-IN"] = False  # 清除登入狀態
    return RedirectResponse(url="/", status_code=303)


# 會員頁
@app.get("/member")
async def member(request: Request):
    if not request.session.get("SIGNED-IN"):  # 檢查使用者是否登入
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("member.html", {"request": request})

# 錯誤頁
@app.get("/error")
async def error(request: Request, message: str):
    # 傳送自定義message並在error page渲染
    return templates.TemplateResponse("error.html", {"request": request, "message": message})

# 計算平方數
@app.get("/square/{number}")
async def square(request: Request, number: int = Path(...)):
    result = number ** 2  
    return templates.TemplateResponse("square.html", {"request": request, "result": result})
