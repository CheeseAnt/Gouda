from src import server
import uvicorn

uvicorn.run(server.app, host="0.0.0.0", port="8120", ssl_certfile="cert.cer", ssl_keyfile="key.pkey")

