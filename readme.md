# OpenCV Video Processing Server
Este proyecto es una aplicación web basada en Flask que permite la transmisión y procesamiento de video en tiempo real utilizando diferentes técnicas de procesamiento de imágenes con OpenCV. La aplicación cuenta con varios endpoints que permiten visualizar el resultado posterior a la aplicación de cada uno de los procesamientos que se indican en el apartado [Endpoints](#endpoints).

Este proyecto ha sido desarrollado por:
- **[Daniel Collaguazo](https://github.com/DanielCollaguazo2003)**
- **[José Villalta](https://github.com/VillaltaJose)**

## Requisitos
- Python 3.7 o superior
- Flask
- OpenCV (`cv2`)
- NumPy
- Requests

## Endpoints

### `/`

Muestra la página principal con el video obtenido de la cámara en el ESP32.

### `/video_stream`
Transmite el video de la cámara en tiempo real sin ningún procesamiento adicional.

### `/video_stream_hist_eq`
Aplica la ecualización de histograma al video en tiempo real.

### `/video_stream_clahe`
Aplica la ecualización de histograma adaptativa (CLAHE) al video.

### `/video_stream_logarithmic`
Aplica un filtro logarítmico al video para mejorar las áreas oscuras.

### `/video_stream_filters`
Aplica filtros de suavizado (mediana, blur, Gaussiano) con diferentes tamaños de máscara al video.

### `/video_stream_motion`
Detecta el movimiento en el video.

### `/video_stream_gray_noise`
Aplica ruido aleatorio a una imagen en escala de grises y muestra la imagen original junto con la imagen con ruido.

### `/video_stream_edge_detection`
Aplica dos algoritmos de detección de bordes (Canny y Sobel) al video. En ambos casos, se aplica la detección con y sin suavizado de imágenes.

### `/morph_operations`
Aplica operaciones morfológicas (erosión, dilatación, Top Hat, Black Hat y una combinación) a imágenes estáticas y muestra los resultados.

Las imágenes se encuentran en el path `static/images`.