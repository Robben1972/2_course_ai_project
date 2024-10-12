from passlib.hash import bcrypt
from sqlalchemy.exc import IntegrityError
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth, OAuthError
from .config import CLIENT_ID, CLIENT_SECRET
from fastapi.staticfiles import StaticFiles
from .model import SessionLocal, User
from fastapi import Form, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="add any string...")
app.mount("/static", StaticFiles(directory="static"), name="static")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


oauth = OAuth()
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    client_kwargs={
        'scope': 'email openid profile',
        'redirect_uri': 'http://localhost:8000/auth'
    }
)

templates = Jinja2Templates(directory="templates")


@app.post("/register")
def register(
        request: Request,
        email: str = Form(...),
        username: str = Form(...),
        password: str = Form(...),
        db: Session = Depends(get_db)
):
    hashed_password = bcrypt.hash(password)
    user = User(email=email, username=username, password=hashed_password)
    try:
        db.add(user)
        db.commit()
        db.refresh(user)

        # Set session data for the newly registered user
        request.session['user'] = {"email": user.email, "username": user.username}

        # Redirect to the welcome page
        url = request.url_for('welcome')
        return RedirectResponse(url, status_code=303)
    except IntegrityError:
        db.rollback()
        return {"error": "Email or Username already exists"}


@app.get("/")
def index(request: Request):
    user = request.session.get('user')
    if user:
        return RedirectResponse('welcome')

    return templates.TemplateResponse(
        name="home.html",
        context={"request": request}
    )


@app.get('/welcome')
def welcome(request: Request):
    user = request.session.get('user')
    if not user:
        return RedirectResponse('/')
    # return templates.TemplateResponse(
    #     name='welcome.html',
    #     context={'request': request, 'user': user}
    # )
    return RedirectResponse(url='https://pdp.uz')


@app.get("/login")
async def login(request: Request):
    redirect_uri = request.url_for('auth')
    return await oauth.google.authorize_redirect(request, redirect_uri)


@app.get('/auth')
async def auth(request: Request, db: Session = Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as e:
        return templates.TemplateResponse(
            name='error.html',
            context={'request': request, 'error': e.error}
        )

    user_info = token.get('userinfo')
    if user_info:
        email = user_info['email']
        username = user_info['name']

        # Check if user exists
        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(email=email, username=username)
            db.add(user)
            db.commit()
            db.refresh(user)

        request.session['user'] = dict(user_info)

    return RedirectResponse('welcome')


@app.get('/logout')
def logout(request: Request):
    request.session.pop('user')
    request.session.clear()
    return RedirectResponse('/')
