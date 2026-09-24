# Informe del proceso: dashboard Viajeros LATAM 2022

**Informe de trabajo — etapa de transferencia.** Autor: Fernando Piñeros Soler. Curso: Programación para Ciencia de Datos II, 2026. Documento de origen: `Pasajeros_Actividades 2 y 4.ipynb` (actividades 2 y 4, y sección 18 de la etapa final).

## 1. Problema, propósito y alcance

El proyecto busca caracterizar y comparar en una base de práctica el perfil y el gasto por registro de viajeros aéreos de Colombia, Brasil, México, Chile, Perú, Argentina y Panamá, y explorar qué aportan los contrastes estadísticos y los modelos estudiados. El dashboard ofrece una exploración interactiva de esos registros para pasar de la comparación general a segmentos específicos.

La base `Base_Viajeros_LATAM_2022.xlsx`, hoja `Datos_Viajeros`, contiene **2.500 filas y 20 variables**, de un único año: 2022. **Los datos son ficticios**. Por ello, los conteos no son estadísticas oficiales ni estimaciones nacionales; tampoco cabe concluir que las diferencias reflejen comportamientos reales de la población. El año constante impide analizar tendencias temporales.

## 2. Trayectoria analítica del cuaderno

1. **Actividad 2:** revisión de la base, descriptivos numéricos y categóricos, cruces y gráficas; regresión simple con distancia y gasto. El cuaderno informa una correlación distancia–gasto de 0,665 y R² de 0,4425 para el ejercicio simple; estas cifras describen la base ficticia y la especificación usada.
2. **Actividad 4, contraste:** comparación del promedio de `Gasto_Total_USD` entre Colombia y el conjunto de los otros seis países mediante t de Welch a dos colas (α = 0,05). El cuaderno consigna medias de USD 344,75 y USD 401,67, respectivamente, con p = 0,000612. Este resultado es una señal estadística **dentro del proceso que generó los datos ficticios**; no prueba una diferencia real entre poblaciones nacionales.
3. **Regresión lineal múltiple:** cinco variables numéricas, división 70/30, con R² de prueba 0,4517 documentado en la sección 15. La mejora frente al ejercicio simple referido como R² 0,4425 es pequeña; la comparación no constituye por sí sola una evaluación controlada de modelos sobre particiones idénticas.
4. **Regresión logística:** clasificación de vuelo doméstico frente a internacional. El cuaderno informa exactitud de prueba de 74,8 % con gasto solo y 84,4 % al agregar variables categóricas, usando divisiones estratificadas 70/30. La exactitud no basta para establecer fiabilidad: también deben revisarse recall, precisión, F1, posible fuga de información y estabilidad de resultados en nuevas particiones.

Estos ejercicios fueron elaborados antes de la interfaz Dash. El tablero actual **no entrena ni recalcula** modelos al aplicar filtros: cinco gráficos muestran estadística descriptiva de la selección activa y un sexto panel reúne como resultados **fijos** el p-valor de Welch, el R² de prueba y las dos exactitudes logísticas de las secciones 14–16 del cuaderno. El panel indica que procede de la base original de 2.500 registros y que sus valores no cambian con los filtros; las particiones y variables se explican en el cuaderno.

## 3. Decisiones de diseño del dashboard

- **Entrada:** el script lee el Excel desde su propia carpeta y verifica 2.500 filas, 20 variables, identificadores únicos y año 2022. De este modo se detecta temprano un archivo equivocado o una modificación del esquema.
- **Unidad de análisis:** un registro por viajero. Las cuatro tarjetas muestran número de registros visibles, número de países, promedio y mediana de `Gasto_Total_USD` por registro. La mediana complementa la media cuando la distribución está sesgada.
- **Filtros conjuntos:** país, motivo, tipo de vuelo y clase tarifaria. Cada vista usa exactamente la misma selección; ninguna opción de un filtro equivale a cero filas. El botón «Restablecer filtros» recupera las cuatro selecciones completas.
- **Cinco gráficos:** conteo por país; media y mediana por país; mediana del gasto por tipo de vuelo, por clase tarifaria y por motivo. En los tres últimos se compara Colombia con los otros países que permanecen visibles y se informa `n` por segmento. Los valores emergentes agregan contexto sin saturar la pantalla.
- **Composición visual:** azul para Colombia, gris para el resto y un esquema inspirado en comunicación aeronáutica, sin adoptar la identidad de una empresa. Cinco gráficas y un sexto panel de evidencia analítica fija se presentan en una cuadrícula de escritorio; en pantallas pequeñas se permite desplazamiento para mantener legibilidad.
- **Narrativa y alcance:** encabezado, explicación de lectura y aviso de naturaleza ficticia en pantalla. No se equipara gasto registrado con ingresos del sector ni se formulan recomendaciones causales sobre países reales.

## 4. Validación realizada

En la sección 18.18, el cuaderno comprueba programáticamente que tarjetas y cinco gráficos son coherentes para: conjunto completo (2.500 registros, 7 países), Colombia (363, 1), Colombia con vuelo internacional (157, 1) y selección de países vacía (0, 0). La vista completa informa media USD 393,41 y mediana USD 290,39; Colombia, media USD 344,75 y mediana USD 238,11. El diseño compacto, los filtros, el botón de reinicio y la apertura local en `http://127.0.0.1:8050/` se revisaron visualmente en el navegador. En la sección 18.25 se añadió el panel fijo y se comprobó visualmente que mantiene p, R² y exactitudes al seleccionar solo Colombia.

Estas comprobaciones validan consistencia funcional y aritmética del dashboard en los escenarios indicados. **No validan exactitud de los datos ficticios frente a fuentes oficiales ni capacidad de generalización de los modelos.**

## 5. Archivos y ejecución local

El Excel, `dashboard_viajeros.py`, `requirements.txt`, `start`, `jupyter_server_config.py` y `README.md` se ubican en una misma carpeta; el cuaderno contiene su construcción paso a paso. En una terminal situada en esa carpeta, `python3 -m pip install -r requirements.txt` instala las dependencias del **dashboard** y `python3 dashboard_viajeros.py` inicia la aplicación local. El archivo `start` está destinado al entorno Binder y no se ejecuta manualmente en Mac.

El repositorio público está en https://github.com/fdopineros63/Viajeros_Latam_2022. El 24 de septiembre de 2026 se comprobó en navegador la apertura del dashboard en Binder con 2.500 registros iniciales, tarjetas, cinco gráficas y panel fijo: https://mybinder.org/v2/gh/fdopineros63/Viajeros_Latam_2022/HEAD?urlpath=viajeros/. El archivo `enlaces_publicacion.txt` contiene ambos enlaces. Esta inspección de la vista inicial no sustituye una evaluación de disponibilidad continua del servicio. Las dependencias históricas para ejecutar **todo** el análisis anterior del cuaderno pueden requerir bibliotecas adicionales (por ejemplo SciPy, scikit-learn, Matplotlib y Seaborn); `requirements.txt` actual está destinado a ejecutar el dashboard.

## 6. Estado y próximos ajustes

La evidencia de contraste y modelos aparece como panel fijo en la interfaz. El repositorio, los enlaces y la apertura inicial en Binder quedaron comprobados. Como trabajo adicional se recomienda revisar la estabilidad de los modelos en particiones nuevas y verificar la ejecución local en otra máquina. Se comprobó la integridad del archivo ZIP de entrega; no se ha realizado una ejecución local en un segundo equipo.

## 7. Conclusiones integradas de las Actividades 2, 4 y 6

La Actividad 2 caracterizó 2.500 registros ficticios y mostró que el gasto cambia según país y segmento de viaje. En Colombia se observó una media de USD 344,75 y una mediana de USD 238,11, frente a una media general de USD 393,41. La asociación distancia–gasto (`r = 0,665`) y la diferencia entre medias y medianas justifican explorar varias variables y presentar tamaños de grupo al interpretar comparaciones.

La Actividad 4 añadió contraste y evaluación predictiva. Welch registró `p = 0,000612` para Colombia frente a los otros seis países dentro de esta base; la regresión múltiple informó `R² de prueba = 0,4517` y los modelos logísticos, exactitudes de prueba de 74,8 % y 84,4 % para las especificaciones simple y ampliada. La mejora de exactitud respalda, dentro de la partición ensayada, el aporte de las variables añadidas. No demuestra validez externa ni causalidad, y las cifras de la regresión simple y múltiple no se obtuvieron mediante una comparación controlada sobre la misma partición.

La Actividad 6 integró los resultados en una vista interactiva. Las tarjetas y cinco gráficas cambian con los cuatro filtros y el botón de restablecimiento; el panel con los tres resultados de modelos conserva las cifras de sus pruebas originales. Esta separación impide atribuir a un segmento filtrado un valor p o una exactitud que no se recalcularon. Las verificaciones de cuatro escenarios y la inspección local respaldan la coherencia funcional documentada; además, se comprobó la apertura de la vista inicial en Binder.

En conjunto se cumplieron los objetivos de caracterizar, comparar, contrastar, modelar y comunicar la base de práctica. El repositorio quedó publicado, la vista inicial funcionó en Binder y ambos enlaces se incluyeron en el archivo de entrega. Dado el origen simulado de los registros, las conclusiones describen únicamente el ejercicio y no constituyen recomendaciones para la industria ni estimaciones sobre viajeros reales.
