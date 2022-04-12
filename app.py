import uvicorn
import shutil
from fastapi import FastAPI, File, UploadFile
import test
import os

from pydub import AudioSegment

import time
import uuid
import tempfile
from starlette.background import BackgroundTask
from io import BytesIO
import librosa


from pathlib import Path
from tempfile import NamedTemporaryFile


app = FastAPI()


@app.post("/predict")
def predict(file: UploadFile = File(...)):

    contents = file.file.read()
    temp = NamedTemporaryFile(delete=False)
    try:
        with temp as f:
            f.write(contents)

        data, samplerate = librosa.load(temp.name)
        prev = test.prev_label(temp.name, data, samplerate)

    finally:
        temp.close()
        os.unlink(temp.name)

    return {"label": prev}
