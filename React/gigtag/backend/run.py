from src import server
import sys
import uvicorn

if len(sys.argv)==1:
    uvicorn.run(server.app, host="0.0.0.0", port=8120, ssl_certfile="cert.cer", ssl_keyfile="key.pkey")
else:
    uvicorn.run(server.app, host="0.0.0.0", port=8120)
