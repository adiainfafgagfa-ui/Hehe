import hashlib
import time
import requests
import asyncio
import os
from telegram import Bot

# ⚠️ Nota Importante: Estos valores NO se ponen directamente aquí.
# Los asignamos a variables de entorno para seguridad en el hosting (Railway).

# 1. Configuración de Seguridad
TOKEN = "8339720336:AAHCS4O_nwwSPopOo1Z1aQOpgj9aexJayG0"
CHAT_ID = "1431962692"
URL_ARCHIVO = "https://frigidus.com/api/get_recent_logins.php"

# 2. Reemplazo por variables de entorno para Railway:
# Debes configurar 'BOT_TOKEN' y 'CHAT_ID_MONITOR' en Railway.
# Si el código se ejecuta localmente, usará los valores hardcodeados para simplicidad.
BOT_TOKEN = os.getenv("BOT_TOKEN", TOKEN)
CHAT_ID_MONITOR = os.getenv("CHAT_ID_MONITOR", CHAT_ID)

# Inicialización del objeto Bot
bot = Bot(token=BOT_TOKEN)

def obtener_hash():
    """Descarga el archivo y calcula su hash SHA256 (Síncrona)."""
    try:
        # Añadimos timeout para evitar bloqueos
        contenido = requests.get(URL_ARCHIVO, timeout=10).text
        return hashlib.sha256(contenido.encode('utf-8')).hexdigest()
    except requests.exceptions.RequestException as e:
        # Esto captura errores de red o timeouts
        print(f"Error al obtener el archivo: {e}")
        return None

# 3. Función Principal Asíncrona con el Bucle de Monitoreo
async def monitorear():
    """Bucle principal que revisa el hash cada 60 segundos."""
    
    hash_anterior = obtener_hash()

    if hash_anterior is None:
        print("Error al obtener el hash inicial. Terminando.")
        # Podríamos intentar enviar un mensaje de error si la inicialización del bot funciona
        await bot.send_message(CHAT_ID_MONITOR, "❌ Error al iniciar: No se pudo acceder al archivo PHP inicialmente.")
        return

    # Envío de mensaje inicial (Debe ser asíncrono: await)
    await bot.send_message(CHAT_ID_MONITOR, "🔍 Monitoreo iniciado. Te avisaré si el archivo cambia.")
    print("Monitoreo iniciado. Hash inicial:", hash_anterior)

    while True:
        await asyncio.sleep(60) # Espera asíncrona de 60 segundos
        
        hash_nuevo = obtener_hash()

        if hash_nuevo is None:
            # Enviamos el mensaje de alerta solo si no se pudo acceder al archivo
            await bot.send_message(CHAT_ID_MONITOR, "⚠️ No pude acceder al archivo.")
            continue

        if hash_nuevo != hash_anterior:
            await bot.send_message(CHAT_ID_MONITOR, "🚨 ¡El archivo PHP ha cambiado!")
            hash_anterior = hash_nuevo
            print(f"¡Cambio detectado! Nuevo hash: {hash_nuevo}")
        else:
            print("Hash sin cambios.")

# 4. Ejecución del Bucle Asíncrono
if __name__ == '__main__':
    if not BOT_TOKEN or not CHAT_ID_MONITOR:
        print("Error: El TOKEN o CHAT_ID no están definidos. Por favor, revisa las variables de entorno.")
    else:
        try:
            # Ejecuta la función asíncrona principal
            asyncio.run(monitorear())
        except Exception as e:
            print(f"Error fatal del bot: {e}")
