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

# Explicación de lo realizado

A continuación se detalla el uso de distintas técnicas de procesamiento de imágenes, incluyendo ecualización de histograma, CLAHE, y un **filtro logarítmico**, así como operaciones morfológicas para mejorar la visualización y claridad en las imágenes.

## 1. Explicación de la Técnica Investigada en Comparación con Ecualización de Histograma y CLAHE
### Ecualización de Histograma
La **ecualización de histograma** es una técnica que mejora el contraste de una imagen al redistribuir la intensidad de los píxeles para que el histograma de la imagen sea más uniforme. Esto es útil para imágenes que presentan un bajo contraste, ya que esta técnica amplía la gama de intensidades, haciendo que detalles en sombras o luces altas sean más visibles. Sin embargo, la ecualización de histograma no es ideal para imágenes con iluminación no homogénea, ya que puede exagerar el ruido en regiones más oscuras o más claras.
![Ecualización de Histograma](https://github.com/user-attachments/assets/e3d7931a-d253-42cf-bd20-6f5337780189)

### CLAHE (Contrast Limited Adaptive Histogram Equalization)
El **CLAHE** es una mejora de la ecualización de histograma que aplica la ecualización de forma adaptativa en pequeñas regiones de la imagen (bloques). Esto permite mejorar el contraste local en áreas específicas sin amplificar el ruido en exceso, ya que limita el contraste en cada bloque.
![CLAHE](https://github.com/user-attachments/assets/06a12d30-e001-4ad9-867c-6c67bc0cf56c)

### Filtro Logarítmico
El **filtro logarítmico** ajusta la escala de intensidad aplicando una transformación logarítmica sobre los valores de los píxeles. Esta técnica reduce la diferencia entre valores de intensidad altos y bajos, haciendo que detalles en las sombras y luces altas sean más visibles. A diferencia de la ecualización de histograma, que redistribuye las intensidades, la transformación logarítmica simplemente disminuye el contraste entre áreas muy brillantes y muy oscuras. Este filtro es especialmente útil en imágenes donde existen áreas brillantes junto a áreas muy oscuras, pero no ofrece un ajuste adaptativo como el CLAHE.
![Filtro Logarítmico](https://github.com/user-attachments/assets/79429927-6891-4bf8-b453-9ab2383e6333)

## 2. Reflexión de resultados de cada filtro
- La **ecualización de histograma** mejoró el contraste general, pero produjo un aumento de ruido en algunas áreas.
- El **CLAHE** proporcionó un mejor resultado al preservar detalles específicos en diferentes partes de la imagen, evitando la exageración de ruido en zonas de bajo contraste.
- El **filtro logarítmico** permitió una mejora en las áreas brillantes y oscuras, pero no ofreció un control adaptativo como el CLAHE, lo que podría limitar su efectividad en algunos escenarios.

### Reflexión sobre los Resultados de Filtros (Mediana, Blur, Gaussiano)

1. **Filtro Mediana**: Este filtro fue efectivo en la reducción del ruido, especialmente en áreas oscuras, preservando los bordes mejor que otros filtros. A medida que aumenta el tamaño de la máscara (5x5, 7x7), la imagen se suaviza más, aunque puede perder algunos detalles finos.

2. **Filtro Blur**: Produce un desenfoque uniforme, pero no maneja el ruido tan bien como el filtro mediana. Con máscaras grandes, la imagen tiende a ser menos nítida, lo que puede afectar la claridad en zonas detalladas.

3. **Filtro Gaussiano**: Logra un equilibrio entre suavizado y preservación de bordes. Con máscaras grandes (5x5 y 7x7), se observa un desenfoque suave sin sacrificar demasiados detalles, lo que ayuda a reducir el ruido de manera uniforme.

## Reflexión sobre los Resultados de las Operaciones Morfológicas

1. **Erosión**: Reduce áreas brillantes y elimina detalles finos. Aunque ayuda a reducir el ruido, puede hacer que estructuras importantes se vean menos definidas.

2. **Dilatación**: Aumenta las áreas brillantes, resaltando bordes y detalles, pero puede hacer que la imagen parezca "ampliada" o borrosa si se usa una máscara grande.

3. **Top Hat**: Resalta estructuras brillantes sobre el fondo oscuro, mejorando la visibilidad de detalles claros. Este filtro fue efectivo para destacar áreas específicas de interés.

4. **Black Hat**: Resalta áreas oscuras en un fondo claro, haciendo más visibles los detalles en sombras o zonas oscuras de la imagen.

5. **Combinación (Top Hat - Black Hat)**: Mejora el contraste general resaltando tanto áreas brillantes como oscuras. Logra un balance en la visibilidad sin amplificar excesivamente el ruido.

### Comparación con la Imagen Original

En comparación con la imagen original, las operaciones morfológicas (especialmente Top Hat y la combinación) mejoraron la nitidez y permitieron observar mejor las estructuras.

![Operaciones Morfológicas en imágenes Médicas](https://github.com/user-attachments/assets/79dce2d6-bf41-44bf-8204-1595bc2944ac)

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

### `/morph_operations/{kernel_size}`
> La variable `kernel_size` es de tipo entero, acepta valores de: `37`, `15`, `7`

Aplica operaciones morfológicas (erosión, dilatación, Top Hat, Black Hat y una combinación) a imágenes estáticas y muestra los resultados.

Las imágenes se encuentran en el path `static/images`.
