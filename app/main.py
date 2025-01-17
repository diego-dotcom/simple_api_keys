from fastapi import FastAPI, HTTPException
from app.database import insert_or_update_api_key
from app.email_utils import send_email
from app.api_key_generator import generate_api_key

app = FastAPI()

@app.post("/generate-api-key/")
async def generate_api_key_endpoint(email: str):
    if "@" not in email:
        raise HTTPException(status_code=400, detail="Email inválido")

    api_key = generate_api_key()

    try:
        # Llamamos a la función para insertar o actualizar la API key
        insert_or_update_api_key(email, api_key)

        # Enviamos el correo con la API key generada
        send_email(email, api_key)
        return {"message": "API key generada y enviada por correo.", "api_key": api_key}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
