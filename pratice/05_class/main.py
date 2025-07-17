import uvicorn
from .server import app


# FastAPI run internally run uvicorn for running application
def main():
    # host "0.0.0.0" means runs on any host
    uvicorn.run(app, port=8000, host="0.0.0.0")


main()
