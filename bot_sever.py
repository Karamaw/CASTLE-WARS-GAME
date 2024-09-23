from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
import random
import time

app = Flask(__name__)

TOKEN = "7748814956:AAFDJsnN_rHNUzU9HZklhKieZFGKIv304zg"  # Asegúrate de tener tu token correcto

# Crear la aplicación de Telegram
application = ApplicationBuilder().token(TOKEN).build()

# Datos del usuario (ejemplo)
usuario_datos = {
    "nivel_castillo": 1,
    "oro": 100,
    "materiales": 0,
    "poder_recoleccion": 1,
    "tiempo_ultima_recompensa": time.time()
}

# Función para calcular la obtención pasiva de oro
def obtener_oro_pasivo():
    tiempo_actual = time.time()
    tiempo_transcurrido = tiempo_actual - usuario_datos["tiempo_ultima_recompensa"]
    oro_obtenido = int(tiempo_transcurrido / 60) * usuario_datos["poder_recoleccion"]
    usuario_datos["oro"] += oro_obtenido
    usuario_datos["tiempo_ultima_recompensa"] = tiempo_actual

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    obtener_oro_pasivo()  # Cada vez que inicie se calcula el oro pasivo
    keyboard = [
        [InlineKeyboardButton("Estado del Castillo", callback_data='estado')],
        [InlineKeyboardButton("Subir Nivel", callback_data='subir_nivel')],
        [InlineKeyboardButton("Realizar Misión", callback_data='misiones')],
        [InlineKeyboardButton("Enfrentamientos", callback_data='enfrentamientos')],
        [InlineKeyboardButton("Buscar Materiales", callback_data='buscar_materiales')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = "¡Bienvenido a tu castillo! Selecciona una opción:"
    await update.message.reply_text(message, reply_markup=reply_markup)

# Manejar las selecciones del menú
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'estado':
        estado = f"Nivel del castillo: {usuario_datos['nivel_castillo']}\nOro: {usuario_datos['oro']}\nMateriales: {usuario_datos['materiales']}"
        await query.edit_message_text(text=estado)

    elif query.data == 'subir_nivel':
        costo_subir_nivel = usuario_datos['nivel_castillo'] * 100
        if usuario_datos['oro'] >= costo_subir_nivel:
            usuario_datos['oro'] -= costo_subir_nivel
            usuario_datos['nivel_castillo'] += 1
            await query.edit_message_text(text=f"Has subido el castillo a nivel {usuario_datos['nivel_castillo']}!")
        else:
            await query.edit_message_text(text="No tienes suficiente oro para subir de nivel.")

    elif query.data == 'misiones':
        recompensa = random.randint(10, 50)
        usuario_datos['oro'] += recompensa
        await query.edit_message_text(text=f"Has completado una misión y ganado {recompensa} monedas de oro!")

    elif query.data == 'enfrentamientos':
        exito = random.choice([True, False])
        if exito:
            recompensa = random.randint(20, 100)
            usuario_datos['oro'] += recompensa
            await query.edit_message_text(text=f"Has ganado el enfrentamiento y obtenido {recompensa} monedas de oro!")
        else:
            await query.edit_message_text(text="Has perdido el enfrentamiento. No ganaste nada.")

    elif query.data == 'buscar_materiales':
        materiales_encontrados = random.randint(1, 5)
        usuario_datos['materiales'] += materiales_encontrados
        await query.edit_message_text(text=f"Has encontrado {materiales_encontrados} materiales.")

# Añadir los manejadores
application.add_handler(CommandHandler('start', start))
application.add_handler(CallbackQueryHandler(button))

# Ruta para manejar las solicitudes POST de Telegram
@app.route(f'/{TOKEN}', methods=['POST'])
def respond():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.process_update(update)
    return 'ok'

# Iniciar el servidor
if __name__ == '__main__':
    print("Servidor Flask está corriendo...")
    app.run(port=5000, debug=True)
