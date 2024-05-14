from typing import Annotated
from fastapi import Depends, FastAPI, Header, HTTPException, Request, Response, status, responses, staticfiles
from fast.auth import is_admin, is_member
from fast.routers import auth, admin, strategies, subscriptions, accounts, portfolio
from db.common import init_db
#from utils.config import get_config_value

init_db()
openapi_url = '/openapi.json' #if get_config_value('enable_openapi_docs') else ''
app = FastAPI(title="main-app", openapi_url=openapi_url)

app.include_router(auth.route, prefix="/api")
app.include_router(strategies.route, prefix="/api", dependencies=[Depends(is_member)])
app.include_router(subscriptions.route, prefix="/api", dependencies=[Depends(is_member)])
app.include_router(accounts.route, prefix="/api", dependencies=[Depends(is_member)])
app.include_router(portfolio.route, prefix="/api", dependencies=[Depends(is_member)])
app.include_router(admin.route, prefix="/api", dependencies=[Depends(is_admin)])

app.mount("/", staticfiles.StaticFiles(directory="../autoinvesting-ui/dist", html=True), name="static") 

"""
@app.middleware('http')
async def client_authentication(request: Request, call_next):
    print('request items: ', request.query_params.items(), request.path_params.items(), request.headers.get('referer'))
    #request.
    client_id = request.headers.get('ClientId') or request.query_params.get('ClientId')
    print('Client id: ', client_id)
    if client_id != get_config_value('client_id'):
        return Response(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
    return await call_next(request)

app.include_router(strategies.router)
app.include_router(ib.router)
app.include_router(connection.router)
"""

# @app.get("/hello")
# def read_root():
#     return {"Hello": "World"}
"""
@app.get("/status")
def get_status_req() -> str:
    try:
        with open(get_config_value('log_dir') + 'live_status.html', 'r') as f:
            statusHtml = f.read()
        return responses.HTMLResponse(content=statusHtml, status_code=200)
    except Exception as e:
        print('Error reading status file: ', e)
        return 'No status available'
"""