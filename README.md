# birdnet-recorder
Record birdsong on your phone, identify species with BirdNET (via birdnetlib).
- `app.py` + `Dockerfile`: FastAPI backend (POST /identify), deploy on Render.
- `web/index.html`: static mobile web app (set API URL), deploy on Vercel.
Models: BirdNET, CC BY-NC-SA 4.0 (non-commercial).
