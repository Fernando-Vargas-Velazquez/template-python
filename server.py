import os
import asyncpg
from pydantic import BaseModel
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from flask import Flask, render_template, send_from_directory, redirect

DATABASE_URL = "postgres://fl0user:nxqSEswz8Z2h@ep-patient-mode-62136438.us-east-2.aws.neon.fl0.io:5432/database?sslmode=require"
conn = None

app = FastAPI()

class Contacto(BaseModel):
    email: str
    nombre: str
    telefono: str

@app.on_event("startup")
async def startup_db_connection():
    global conn
    conn = await asyncpg.connect(DATABASE_URL)
    await create_table()

@app.on_event("shutdown")
async def shutdown_db_connection():
    await conn.close()

@app.post("/contactos")
async def crear_contacto(contacto: Contacto):
    await conn.execute('INSERT INTO contactos (email, nombre, telefono) VALUES ($1, $2, $3)',
                      contacto.email, contacto.nombre, contacto.telefono)
    return contacto

@app.get("/contactos")
async def obtener_contactos():
    rows = await conn.fetch('SELECT * FROM contactos')
    return [dict(row) for row in rows]

@app.get("/contactos/{email}")
async def obtener_contacto(email: str):
    row = await conn.fetchrow('SELECT * FROM contactos WHERE email = $1', email)
    return dict(row) if row else None

@app.put("/contactos/{email}")
async def actualizar_contacto(email: str, contacto: Contacto):
    await conn.execute('UPDATE contactos SET nombre = $1, telefono = $2 WHERE email = $3',
                      contacto.nombre, contacto.telefono, email)
    return contacto.dict()

@app.delete("/contactos/{email}")
async def eliminar_contacto(email: str):
    await conn.execute('DELETE FROM contactos WHERE email = $1', email)
    return {"message": "Contacto eliminado"}

flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return render_template('index.html')

@flask_app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

@flask_app.route('/<path:path>')
def all_routes(path):
    return redirect('/')

async def create_table():
    create_table_query = '''
        CREATE TABLE IF NOT EXISTS contactos (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255),
            nombre VARCHAR(255),
            telefono VARCHAR(20)
        )
    '''
    await conn.execute(create_table_query)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)
