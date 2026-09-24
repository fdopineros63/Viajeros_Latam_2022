# Dashboard Viajeros LATAM 2022

Tablero interactivo para explorar una **base ficticia** de 2.500 registros de viajeros de siete países en 2022. Cada fila es un registro de viajero; los resultados describen únicamente esta base de práctica y no estiman el comportamiento real de la población latinoamericana.

## Archivos necesarios

Coloque juntos en la misma carpeta:

- `dashboard_viajeros.py`: aplicación Dash y cálculos de las visualizaciones.
- `Base_Viajeros_LATAM_2022.xlsx`: datos originales; hoja `Datos_Viajeros`.
- `requirements.txt`: dependencias de Python.

El cuaderno `Pasajeros_Actividades 2 y 4.ipynb` documenta la construcción y comprobación del tablero. No es necesario ejecutar el cuaderno para usar la aplicación si ya está presente el archivo `.py`.

## Ejecutar en computador propio

Abra una terminal **dentro de esa carpeta** y ejecute:

```bash
python3 -m pip install -r requirements.txt
python3 dashboard_viajeros.py
```

Abra `http://127.0.0.1:8050/` en el navegador. Mantenga abierta la terminal mientras use el tablero. Para detenerlo, pulse **Control+C**. El proyecto se ha usado con Python 3.10; la instalación en otra máquina se comprobará en una etapa posterior.

## Cómo explorarlo

Los cuatro filtros permiten escoger una o varias opciones de **país, motivo de viaje, tipo de vuelo y clase tarifaria**. Se combinan: cada gráfico y tarjeta muestra los registros que cumplen todas las selecciones. Si deja un filtro sin opciones, se muestran cero registros y «Sin datos» en los indicadores de gasto. Pulse **Restablecer filtros** para volver a seleccionar todas las opciones y recuperar la vista de 2.500 registros.

Las cuatro tarjetas muestran registros visibles, países visibles y gasto promedio y mediano por registro (USD). Las cinco gráficas presentan registros por país, gasto medio y mediano por país, gasto mediano según tipo de vuelo, clase tarifaria y motivo de viaje. En las comparaciones agrupadas, azul identifica a Colombia y gris a los demás países visibles. Al pasar el cursor aparece el tamaño de cada grupo y más detalle. Un sexto panel presenta resultados **fijos de la base completa**: Welch (p = 0,000612), R² de prueba de la regresión lineal múltiple (0,4517) y exactitud logística simple y ampliada (74,8 % y 84,4 %). Estas métricas proceden de las secciones 14–16 del cuaderno; **no se recalculan** al usar los filtros.

En pantallas de escritorio se muestran conjuntamente indicadores y gráficas; en dispositivos más pequeños se puede desplazar la página para preservar legibilidad. Las cifras por país son conteos de registros de esta base y **no tasas de viajeros de esos países**. El gasto es por registro, no una suma de ingresos ni un pronóstico.

## Comprobaciones realizadas y alcance

El cuaderno, en su sección 18.18, comprueba filtros, indicadores y cinco gráficas con base completa (2.500 registros y 7 países), solo Colombia (363 y 1), Colombia con vuelo internacional (157 y 1) y selección vacía (0 y 0). También se revisaron en el navegador los filtros, el botón de reinicio y que el panel fijo no cambie al seleccionar solo Colombia. Estas pruebas comprueban coherencia interna; la base ficticia no permite inferencias sobre viajeros reales.

## Diseño visual

La paleta es propia del proyecto, inspirada en el uso de azules y blancos en comunicación aeronáutica, sin reproducir la marca de una compañía. Referencias: [paleta corporativa de Airbus](https://www.brand.airbus.com/en/asset-library/colours) e [historia de la bandera de la OACI](https://www.icao.int/sites/default/files/postalhistory/the_icao_flag.htm).

## Binder (pendiente de publicación y prueba)

`start` y `jupyter_server_config.py` preparan el arranque de Dash detrás del proxy de Jupyter. Una vez que **los archivos vigentes** estén en la raíz de un repositorio público de GitHub, el enlace previsto usará el sufijo `?urlpath=viajeros/`. Hasta comprobarlo en un repositorio real, no se debe presentar ese enlace como funcionando. No ejecute manualmente `start` al abrir el dashboard en su computador.
