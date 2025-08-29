import cv2
import dlib
import time
import math
import threading
import numpy as np
from collections import deque
from flask import Flask, render_template
from flask_socketio import SocketIO
from scipy.spatial import distance as dist

# =========================
# Config Flask + Socket.IO
# =========================
app = Flask(__name__)
socketio = SocketIO(app, async_mode='threading', cors_allowed_origins="*")

# ================
# Detección: estado
# ================
lock = threading.Lock()

stats = {
    "yawns_total": 0,
    "eye_closures_total": 0,
    "alerts_total": 0
}

# Para el frontend (últimos eventos visibles)
events = deque(maxlen=50)  # p.ej. "😮 Bostezo", "⚠️ Ojos cerrados 2s", etc.

# Para lógica de bostezos (ventana temporal)
yawn_times = deque()  # timestamps de bostezos confirmados

# =========================
# Umbrales y parámetros
# =========================
# OJOS (EAR)
EYE_AR_THRESH = 0.23              # Umbral de ojos cerrados (ajusta 0.20–0.25)
EYE_AR_HYST = 0.02                # Histéresis para evitar parpadeos en el umbral
EYE_AR_CONSEC_FRAMES = 12         # Frames consecutivos por debajo para evento (ajusta a tu FPS)

# BOCA (MAR)
MAR_OPEN = 0.70                   # Umbral de boca ABIERTA para empezar bostezo (ajusta 0.65–0.8)
MAR_CLOSE = 0.55                  # Umbral de boca CERRADA para terminar bostezo
YAWN_MIN_OPEN_TIME = 0.5          # Segs mínimos boca abierta para contar bostezo
YAWN_SERIES_COUNT = 3             # Nº de bostezos en ventana => alerta
YAWN_SERIES_WINDOW = 8.0          # Segs de ventana para "varios en poco tiempo"

# Otras protecciones
MAX_FACES = 1                     # tomamos la cara más grande
EMIT_STATS_EVERY = 0.5            # segs: frecuencia de envío de stats al dashboard

# =========================
# Utilidades geométricas
# =========================
def eye_aspect_ratio(eye):
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3]) + 1e-6
    return (A + B) / (2.0 * C)

def mouth_aspect_ratio(mouth):
    A = dist.euclidean(mouth[2], mouth[10])  # 51-59
    B = dist.euclidean(mouth[4], mouth[8])   # 53-57
    C = dist.euclidean(mouth[0], mouth[6]) + 1e-6  # 49-55
    return (A + B) / (2.0 * C)

# =========================
# Hilo de detección
# =========================
def detection_loop():
    global stats, events, yawn_times

    # Modelos dlib
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # CAP_DSHOW ayuda en Windows
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    # Índices 68-landmarks
    L_EYE = slice(42, 48)  # ojo izquierdo
    R_EYE = slice(36, 42)  # ojo derecho
    MOUTH = slice(48, 68)  # boca

    # Estado de ojos
    eye_counter = 0
    eye_episode_active = False  # si ya contamos un "cierre prolongado" y esperamos que se abra

    # Estado de bostezo
    yawn_open = False
    yawn_open_start = 0.0

    last_emit = 0.0

    while True:
        ok, frame = cap.read()
        if not ok:
            time.sleep(0.05)
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rects = detector(gray, 0)

        # Seleccionar la cara más grande (si hay varias)
        if len(rects) > 1:
            rects = sorted(rects, key=lambda r: r.width() * r.height(), reverse=True)[:MAX_FACES]

        if len(rects) == 0:
            # reset rápido para episodios
            eye_counter = 0
            eye_episode_active = False
            now = time.time()
            if now - last_emit >= EMIT_STATS_EVERY:
                with lock:
                    print("Enviando stats (sin cara):", stats)
                    print("Enviando eventos (sin cara):", list(events)[-20:])
                    socketio.emit("stats", stats)
                    socketio.emit("events", list(events)[-20:])
                last_emit = now
            cv2.imshow("Driver Monitoring", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            continue

        rect = rects[0]
        shape = predictor(gray, rect)
        pts = np.array([(shape.part(i).x, shape.part(i).y) for i in range(68)], dtype=np.float32)

        # EAR
        left_eye = pts[L_EYE]
        right_eye = pts[R_EYE]
        ear_left = eye_aspect_ratio(left_eye)
        ear_right = eye_aspect_ratio(right_eye)
        ear = (ear_left + ear_right) / 2.0

        # MAR
        mouth = pts[MOUTH]
        mar = mouth_aspect_ratio(mouth)

        # -------- OJOS: cierre prolongado con histéresis --------
        eye_close_threshold = EYE_AR_THRESH
        eye_open_threshold  = EYE_AR_THRESH + EYE_AR_HYST

        if not eye_episode_active:
            # Aún no contamos este episodio
            if ear < eye_close_threshold:
                eye_counter += 1
                if eye_counter >= EYE_AR_CONSEC_FRAMES:
                    # Evento: cierre prolongado
                    with lock:
                        stats["eye_closures_total"] += 1
                        stats["alerts_total"] += 1
                        events.append("👀 Cierre de ojos prolongado")
                    print("⚠️ Cierre de ojos prolongado")
                    eye_episode_active = True
                    eye_counter = 0
            else:
                eye_counter = 0
        else:
            # Ya contamos el episodio, esperamos a que se "abra" para rearmar
            if ear > eye_open_threshold:
                eye_episode_active = False
                eye_counter = 0

        # -------- BOSTEZO: estado abrir->cerrar + duración mínima + ventana --------
        now = time.time()
        if not yawn_open:
            if mar >= MAR_OPEN:
                yawn_open = True
                yawn_open_start = now
        else:
            # Estamos en "boca abierta"
            # Dos formas de cerrar el bostezo: MAR baja de MAR_CLOSE o llevamos mucho abiertos y baja un poco
            if mar <= MAR_CLOSE:
                open_time = now - yawn_open_start
                yawn_open = False
                if open_time >= YAWN_MIN_OPEN_TIME:
                    # Confirmar bostezo
                    with lock:
                        stats["yawns_total"] += 1
                        events.append("😮 Bostezo confirmado")
                    print("😮 Bostezo confirmado (duración: %.2fs)" % open_time)
                    # Ventana de serie
                    yawn_times.append(now)
                    # limpiar ventana
                    while yawn_times and (now - yawn_times[0] > YAWN_SERIES_WINDOW):
                        yawn_times.popleft()
                    if len(yawn_times) >= YAWN_SERIES_COUNT:
                        with lock:
                            stats["alerts_total"] += 1
                            events.append("⚠️ Demasiados bostezos en poco tiempo")
                        print("⚠️ Alerta: Demasiados bostezos en %ds" % YAWN_SERIES_WINDOW)
                        yawn_times.clear()

        # -------- Overlay visual opcional --------
        cv2.putText(frame, f"EAR: {ear:.2f}", (10, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (40, 220, 40), 2)
        cv2.putText(frame, f"MAR: {mar:.2f}", (10, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (40, 220, 220), 2)

        with lock:
            cv2.putText(frame, f"Bostezos: {stats['yawns_total']}", (10, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 0), 2)
            cv2.putText(frame, f"Cierres ojos: {stats['eye_closures_total']}", (10, 105),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 200, 255), 2)
            cv2.putText(frame, f"Alertas: {stats['alerts_total']}", (10, 130),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 80, 255), 2)

        # Envío periódico de stats (no cada frame)
        if now - last_emit >= EMIT_STATS_EVERY:
            with lock:
                print("Enviando stats:", stats)
                print("Enviando eventos:", list(events)[-20:])
                socketio.emit("stats", stats)
                socketio.emit("events", list(events)[-20:])
            last_emit = now

        cv2.imshow("Driver Monitoring", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# =========================
# Rutas Flask
# =========================
@app.route("/")
def index():
    return render_template("index.html")

# =========================
# Main
# =========================
if __name__ == "__main__":
    t = threading.Thread(target=detection_loop, daemon=True)
    t.start()
    # Ejecuta el servidor web
    socketio.run(app, host="0.0.0.0", port=5000, debug=False)
