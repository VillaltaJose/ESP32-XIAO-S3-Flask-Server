from flask import Flask, render_template, Response, stream_with_context, Request
from io import BytesIO

import time
import cv2
import numpy as np
import requests
import base64

app = Flask(__name__)
# IP Address
_URL = 'http://192.168.1.13'
# Default Streaming Port
_PORT = '81'
# Default streaming route
_ST = '/stream'
SEP = ':'

stream_url = ''.join([_URL,SEP,_PORT,_ST])

def video_capture():
    res = requests.get(stream_url, stream=True)
    for chunk in res.iter_content(chunk_size=100000):
        if len(chunk) > 100:
            try:
                img_data = np.frombuffer(chunk, np.uint8)
                cv_img = cv2.imdecode(img_data, cv2.IMREAD_COLOR)
                if cv_img is None:
                    continue
                yield cv_img
            except Exception as e:
                print("Error al procesar el frame:", e)
                continue

def return_frame(frame):
    return frame

def apply_gray_noise(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    N = 537
    height, width = gray.shape
    noise = np.zeros((height, width), dtype=np.uint8)
    random_positions = (np.random.randint(0, height, N), np.random.randint(0, width, N))
    noise[random_positions[0], random_positions[1]] = 255
    noise_image = cv2.bitwise_or(gray, noise)
    total_image = np.zeros((height, width * 2), dtype=np.uint8)
    total_image[:, :width] = gray
    total_image[:, width:] = noise_image
    return total_image

# Función para ecualización de histograma
def apply_hist_eq(frame):
    cielab = cv2.cvtColor(frame, cv2.COLOR_BGR2Lab)
    channels = list(cv2.split(cielab))

    if channels[0].dtype != np.uint8:
        channels[0] = channels[0].astype(np.uint8)

    channels[0] = cv2.equalizeHist(channels[0])
    hist_eq_img = cv2.merge(channels)
    res = cv2.cvtColor(hist_eq_img, cv2.COLOR_Lab2BGR)

    return np.hstack((frame, res))

# Función para ecualización de histograma CLAHE
def apply_clahe(cv_img, limit=40):
    cielab = cv2.cvtColor(cv_img, cv2.COLOR_BGR2Lab)
    channels = list(cv2.split(cielab))
    
    if channels[0].dtype != np.uint8:
        channels[0] = channels[0].astype(np.uint8)
    
    clahe = cv2.createCLAHE(clipLimit=limit, tileGridSize=(8, 8))
    channels[0] = clahe.apply(channels[0])
    
    clahe_img = cv2.merge(channels)
    res = cv2.cvtColor(clahe_img, cv2.COLOR_Lab2BGR)
    return np.hstack((cv_img, res))

def apply_logarithmic_filter(frame):
    cielab = cv2.cvtColor(frame, cv2.COLOR_BGR2Lab)
    channels = list(cv2.split(cielab))

    logL = channels[0].astype(np.float32) + 1  # +1 para evitar log(0)
    logL = np.log(logL)

    cv2.normalize(logL, logL, 0, 255, cv2.NORM_MINMAX)
    logL = logL.astype(np.uint8)

    channels[0] = logL
    cielab_log = cv2.merge(channels)
    logaritmica = cv2.cvtColor(cielab_log, cv2.COLOR_Lab2BGR)

    return np.hstack((frame, logaritmica))

def apply_filters(frame, kernel_sizes=[3, 5, 7]):
    results = []
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    for size in kernel_sizes:
        median = cv2.medianBlur(gray_frame, size)
        cv2.putText(median, f"Mediana {size}x{size}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, 255, 2)

        blur = cv2.blur(gray_frame, (size, size))
        cv2.putText(blur, f"Blur {size}x{size}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, 255, 2)

        gaussian = cv2.GaussianBlur(gray_frame, (size, size), 0)
        cv2.putText(gaussian, f"Gaussiano {size}x{size}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, 255, 2)

        row = np.hstack((median, blur, gaussian))
        results.append(row)

    combined_result = np.vstack(results)
    return combined_result

# Función para detectar movimiento
def detect_motion(prev_frame, current_frame, threshold=30):
    gray_prev = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    gray_current = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)
    diff = cv2.absdiff(gray_prev, gray_current)
    _, motion_mask = cv2.threshold(diff, threshold, 255, cv2.THRESH_BINARY)
    if cv2.countNonZero(motion_mask) > 100:
        cv2.putText(motion_mask, "Movimiento detectado!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, 255, 2)
    return motion_mask

# Función para enviar el stream con diferentes rutas
def generate_frames(process_function):
    prev_frame = None
    last_time = time.time()
    fps = 0

    for frame in video_capture():
        current_time = time.time()
        if prev_frame is not None:
            fps = 1 / (current_time - last_time)
            last_time = current_time

            processed_frame = process_function(prev_frame, frame) if process_function == detect_motion else process_function(frame)

            cv2.putText(processed_frame, f"FPS: {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

            flag, encoded_image = cv2.imencode(".jpg", processed_frame)
            if not flag:
                continue

            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encoded_image) + b'\r\n')

        prev_frame = frame
        last_time = current_time

def apply_morph_operations(image, kernel_size):
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    erosion = cv2.erode(image, kernel, iterations=1)
    dilation = cv2.dilate(image, kernel, iterations=1)
    top_hat = cv2.morphologyEx(image, cv2.MORPH_TOPHAT, kernel)
    black_hat = cv2.morphologyEx(image, cv2.MORPH_BLACKHAT, kernel)
    combined = cv2.add(image, cv2.subtract(top_hat, black_hat))
    
    return {
        "original": image,
        "erosion": erosion,
        "dilation": dilation,
        "top_hat": top_hat,
        "black_hat": black_hat,
        "combined": combined
    }

def apply_edge_detection(frame):
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred_frame = cv2.GaussianBlur(gray_frame, (5, 5), 0)

    canny = cv2.Canny(gray_frame, 100, 200)
    sobel = cv2.Sobel(gray_frame, cv2.CV_64F, 1, 1, ksize=5)
    sobel = cv2.convertScaleAbs(sobel)

    canny_blurred = cv2.Canny(blurred_frame, 100, 200)
    sobel_blurred = cv2.Sobel(blurred_frame, cv2.CV_64F, 1, 1, ksize=5)
    sobel_blurred = cv2.convertScaleAbs(sobel_blurred)

    top = np.hstack((gray_frame, canny, sobel))
    bottom = np.hstack((blurred_frame, canny_blurred, sobel_blurred))
    combined_result = np.vstack((top, bottom))

    return combined_result

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/video_stream")
def video_stream():
    return Response(generate_frames(return_frame),
                    mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/video_stream_hist_eq")
def video_stream_hist_eq():
    return Response(generate_frames(apply_hist_eq),
                    mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/video_stream_clahe")
def video_stream_clahe():
    return Response(generate_frames(apply_clahe),
                    mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/video_stream_logarithmic")
def video_stream_logarithmic():
    return Response(generate_frames(apply_logarithmic_filter),
                    mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/video_stream_filters")
def video_stream_filters():
    return Response(generate_frames(apply_filters),
                    mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/video_stream_motion")
def video_stream_motion():
    return Response(generate_frames(detect_motion),
                    mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/video_stream_gray_noise")
def video_stream_gray_noise():
    return Response(generate_frames(apply_gray_noise),
                    mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/video_stream_edge_detection")
def video_stream_edge_detection():
    return Response(generate_frames(apply_edge_detection),
                    mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/morph_operations/<int:kernel_size>")
def morph_operations(kernel_size):
    if kernel_size not in [37, 15, 7]:
        return "Tamaño de kernel no válido. Usa 37, 15, o 7.", 400
    
    IMAGES = ["./static/images/image1.jpg", "./static/images/image2.jpg", "./static/images/image3.jpg"]

    processed_images = {}
    for idx, image_path in enumerate(IMAGES):
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            return f"Error al cargar la imagen {image_path}", 500
        
        results = apply_morph_operations(image, kernel_size)
        processed_images[f"image_{idx+1}"] = results

    html_content = "<h1>Operaciones Morfológicas</h1>"
    html_content += "<table>"
    for image_key, operations in processed_images.items():
        html_content += "<tr><th colspan='6'>{}</th></tr>".format(image_key)
        html_content += "<tr><th>Original</th><th>Erosión</th><th>Dilatación</th><th>Top Hat</th><th>Black Hat</th><th>Combinada</th></tr>"
        html_content += "<tr>"
        for op_name, img in operations.items():
            _, buffer = cv2.imencode(".png", img)
            encoded_img = base64.b64encode(buffer).decode('utf-8')
            html_content += f'<td><img src="data:image/png;base64,{encoded_img}" alt="{op_name}" style="width: 100%"></td>'
        html_content += "</tr>"
    html_content += "</table>"

    return html_content

if __name__ == "__main__":
    app.run(debug=False)
