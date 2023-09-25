import asyncio
import tempfile

from fastapi import FastAPI, UploadFile

app = FastAPI()


@app.post("/decompile/")
async def decompile(file: UploadFile):
    with tempfile.NamedTemporaryFile() as local_copy:
        local_copy.write(await file.read())
        local_copy.seek(0)

        output = await asyncio.create_subprocess_exec(
            "ilspycmd",
            f"{local_copy.name}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await output.communicate()

    return {
        "stdout": stdout,
        "stderr": stderr,
    }
