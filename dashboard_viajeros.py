"""Tablero de Viajeros LATAM 2022: evidencia analítica fija (18.25)."""

import os
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from dash import Dash, Input, Output, dcc, html


RUTA_BASE = Path(__file__).resolve().parent / "Base_Viajeros_LATAM_2022.xlsx"
if not RUTA_BASE.is_file():
    raise FileNotFoundError(f"Coloque {RUTA_BASE.name} junto a este script.")
datos = pd.read_excel(RUTA_BASE, sheet_name="Datos_Viajeros", header=3)
assert datos.shape == (2500, 20), "La estructura de la base cambió."
assert datos["Viajero_ID"].is_unique and datos["Anio"].eq(2022).all()

CAMPOS = {
    "pais": ("Pais", "País"),
    "motivo": ("Motivo_Viaje", "Motivo de viaje"),
    "vuelo": ("Tipo_Vuelo", "Tipo de vuelo"),
    "clase": ("Clase_Tarifaria", "Clase tarifaria"),
}
ETIQUETAS = {
    "Economica": "Económica",
    "Familiar_Visita": "Visita familiar",
    "Domestico": "Doméstico",
    "Premium_Economy": "Premium Economy",
}

# Paleta original inspirada en cielo y señalética aeronáutica; no es marca ajena.
AZUL_NOCHE = "#102A43"
AZUL_AEREO = "#1769AA"
AZUL_CIELO = "#79BDE8"
GRIS_ALA = "#A6B8C8"


def compactar(fig, titulo, lateral=48, leyenda=False):
    """Márgenes y tipografía para paneles de dos filas sin perder detalle al pasar el cursor."""
    fig.update_layout(
        title=dict(text=titulo, font=dict(size=14, color=AZUL_NOCHE), x=0.02, y=0.97),
        autosize=True, height=None, margin=dict(l=lateral, r=18, t=34, b=32),
        template="plotly_white", font=dict(size=10, color=AZUL_NOCHE),
        paper_bgcolor="white", plot_bgcolor="white",
        showlegend=leyenda, legend=dict(orientation="h", x=0, y=1.01,
                                         font=dict(size=10), bgcolor="rgba(255,255,255,.75)"),
        xaxis=dict(title=None, automargin=True, tickfont=dict(size=9),
                   gridcolor="#E8F0F7"),
        yaxis=dict(title=None, automargin=True, tickfont=dict(size=9),
                   gridcolor="#E8F0F7"),
    )
    return fig


def filtrar(datos_base, selecciones):
    """Lista completa = todos los valores; lista vacía = cero registros."""
    mascara = pd.Series(True, index=datos_base.index)
    for clave, (columna, _) in CAMPOS.items():
        mascara &= datos_base[columna].isin(selecciones[clave] or [])
    return datos_base.loc[mascara]


def indicadores(vista):
    """Cuatro tarjetas; los gastos quedan ausentes si la selección está vacía."""
    return (len(vista), vista["Pais"].nunique(),
            vista["Gasto_Total_USD"].mean() if len(vista) else None,
            vista["Gasto_Total_USD"].median() if len(vista) else None)


def grafico_paises(vista):
    """Registros por país de la misma selección que alimenta las tarjetas."""
    conteos = vista.groupby("Pais")["Viajero_ID"].count().sort_values(ascending=False)
    assert int(conteos.sum()) == len(vista)
    fig = go.Figure()
    if conteos.empty:
        fig.add_annotation(text="No hay registros para esta selección",
                           x=0.5, y=0.5, xref="paper", yref="paper",
                           showarrow=False, font_size=17)
    else:
        fig.add_bar(x=conteos.to_numpy(), y=conteos.index.tolist(),
                    orientation="h", text=conteos.to_numpy(), textposition="outside",
                    marker_color=[AZUL_AEREO if pais == "Colombia" else GRIS_ALA
                                  for pais in conteos.index],
                    hovertemplate="%{y}: %{x:,} registros<extra></extra>")
    fig.update_layout(title="Registros de viajeros por país (base ficticia, 2022)",
                      xaxis_title="Número de registros visibles", yaxis_title="País",
                      yaxis=dict(autorange="reversed"), template="plotly_white",
                      height=440, margin=dict(l=100, r=70, t=75, b=60))
    return compactar(fig, "Viajeros por país · n", lateral=62)


def grafico_gasto_paises(vista):
    """Media y mediana por registro para cada país visible."""
    resumen = (vista.groupby("Pais")["Gasto_Total_USD"]
               .agg(n="size", promedio="mean", mediana="median")
               .sort_values("n", ascending=False))
    assert int(resumen["n"].sum()) == len(vista)
    fig = go.Figure()
    if resumen.empty:
        fig.add_annotation(text="No hay registros para esta selección",
                           x=0.5, y=0.5, xref="paper", yref="paper",
                           showarrow=False, font_size=17)
    else:
        for columna, nombre, simbolo, color in [
            ("promedio", "Promedio", "circle", AZUL_NOCHE),
            ("mediana", "Mediana", "diamond", GRIS_ALA),
        ]:
            colores = [AZUL_AEREO if pais == "Colombia" and columna == "promedio"
                       else AZUL_CIELO if pais == "Colombia" else color
                       for pais in resumen.index]
            fig.add_scatter(
                x=resumen[columna].to_numpy(), y=resumen.index.tolist(),
                mode="markers", name=nombre,
                marker=dict(symbol=simbolo, size=9, color=colores),
                customdata=resumen["n"].to_numpy(),
                hovertemplate=(f"%{{y}} · {nombre}: USD %{{x:,.2f}}"
                               "<br>Registros: %{customdata:,}<extra></extra>"),
            )
    fig.update_layout(title="Gasto por registro: promedio y mediana según país (2022)",
                      xaxis_title="Gasto_Total_USD por registro", yaxis_title="País",
                      yaxis=dict(autorange="reversed"), template="plotly_white",
                      height=460, margin=dict(l=100, r=55, t=80, b=65))
    return compactar(fig, "Gasto por país · media y mediana USD", lateral=62, leyenda=True)


def grafico_tipo_vuelo(vista):
    """Gasto mediano por tipo de vuelo en Colombia y otros países visibles."""
    grupos = vista.assign(Grupo=vista["Pais"].eq("Colombia").map(
        {True: "Colombia", False: "Otros países visibles"}))
    resumen = (grupos.groupby(["Grupo", "Tipo_Vuelo"])["Gasto_Total_USD"]
               .agg(n="size", promedio="mean", mediana="median").reset_index())
    assert int(resumen["n"].sum()) == len(vista)
    fig = go.Figure()
    if resumen.empty:
        fig.add_annotation(text="No hay registros para esta selección",
                           x=0.5, y=0.5, xref="paper", yref="paper",
                           showarrow=False, font_size=17)
    else:
        for grupo, color in [("Colombia", AZUL_AEREO),
                             ("Otros países visibles", GRIS_ALA)]:
            filas = resumen.loc[resumen["Grupo"].eq(grupo)]
            if filas.empty:
                continue
            fig.add_bar(
                x=[ETIQUETAS.get(tipo, tipo) for tipo in filas["Tipo_Vuelo"]],
                y=filas["mediana"].to_numpy(), name=grupo, marker_color=color,
                text=filas["n"].map(lambda n: f"n={n}"),
                textposition="outside", cliponaxis=False,
                customdata=filas[["n", "promedio"]].to_numpy(),
                hovertemplate=(f"<b>{grupo} · %{{x}}</b>"
                               "<br>Mediana: USD %{y:,.2f}"
                               "<br>Promedio: USD %{customdata[1]:,.2f}"
                               "<br>Registros: %{customdata[0]:,.0f}<extra></extra>"),
            )
    fig.update_layout(title="Gasto mediano por tipo de vuelo (base ficticia, 2022)",
                      xaxis_title="Tipo de vuelo",
                      xaxis=dict(categoryorder="array", categoryarray=["Doméstico", "Internacional"]),
                      yaxis_title="Mediana de Gasto_Total_USD por registro",
                      barmode="group", template="plotly_white", height=460,
                      margin=dict(l=80, r=55, t=80, b=65))
    return compactar(fig, "Gasto mediano · tipo de vuelo", leyenda=True)


def grafico_clase(vista):
    """Mediana de gasto por clase para Colombia y otros países visibles."""
    grupos = vista.assign(Grupo=vista["Pais"].eq("Colombia").map(
        {True: "Colombia", False: "Otros países visibles"}))
    resumen = (grupos.groupby(["Grupo", "Clase_Tarifaria"])["Gasto_Total_USD"]
               .agg(n="size", promedio="mean", mediana="median").reset_index())
    assert int(resumen["n"].sum()) == len(vista)
    if not resumen.empty:
        resumen["porcentaje"] = (100 * resumen["n"] /
                                 resumen.groupby("Grupo")["n"].transform("sum"))
    fig = go.Figure()
    if resumen.empty:
        fig.add_annotation(text="No hay registros para esta selección",
                           x=0.5, y=0.5, xref="paper", yref="paper",
                           showarrow=False, font_size=17)
    else:
        for grupo, color in [("Colombia", AZUL_AEREO),
                             ("Otros países visibles", GRIS_ALA)]:
            filas = resumen.loc[resumen["Grupo"].eq(grupo)]
            if filas.empty:
                continue
            fig.add_bar(
                x=[ETIQUETAS.get(clase, clase) for clase in filas["Clase_Tarifaria"]],
                y=filas["mediana"].to_numpy(), name=grupo, marker_color=color,
                text=filas["n"].map(lambda n: f"n={n}"),
                textposition="outside", cliponaxis=False,
                customdata=filas[["n", "promedio", "porcentaje"]].to_numpy(),
                hovertemplate=(f"<b>{grupo} · %{{x}}</b>"
                               "<br>Mediana: USD %{y:,.2f}"
                               "<br>Promedio: USD %{customdata[1]:,.2f}"
                               "<br>Registros: %{customdata[0]:,.0f}"
                               "<br>Parte del grupo visible: %{customdata[2]:.1f}%<extra></extra>"),
            )
    fig.update_layout(
        title="Gasto mediano por clase tarifaria (base ficticia, 2022)",
        xaxis_title="Clase tarifaria",
        xaxis=dict(categoryorder="array",
                   categoryarray=["Económica", "Premium Economy", "Ejecutiva"]),
        yaxis_title="Mediana de Gasto_Total_USD por registro",
        barmode="group", template="plotly_white", height=460,
        margin=dict(l=80, r=55, t=80, b=65))
    return compactar(fig, "Gasto mediano · clase tarifaria", leyenda=True)


def grafico_motivo(vista):
    """Mediana de gasto por motivo para Colombia y otros países visibles."""
    grupos = vista.assign(Grupo=vista["Pais"].eq("Colombia").map(
        {True: "Colombia", False: "Otros países visibles"}))
    resumen = (grupos.groupby(["Grupo", "Motivo_Viaje"])["Gasto_Total_USD"]
               .agg(n="size", promedio="mean", mediana="median").reset_index())
    assert int(resumen["n"].sum()) == len(vista)
    if not resumen.empty:
        resumen["porcentaje"] = (100 * resumen["n"] /
                                 resumen.groupby("Grupo")["n"].transform("sum"))
    fig = go.Figure()
    if resumen.empty:
        fig.add_annotation(text="No hay registros para esta selección",
                           x=0.5, y=0.5, xref="paper", yref="paper",
                           showarrow=False, font_size=17)
    else:
        for grupo, color in [("Colombia", AZUL_AEREO),
                             ("Otros países visibles", GRIS_ALA)]:
            filas = resumen.loc[resumen["Grupo"].eq(grupo)]
            if filas.empty:
                continue
            fig.add_bar(
                x=[ETIQUETAS.get(motivo, motivo) for motivo in filas["Motivo_Viaje"]],
                y=filas["mediana"].to_numpy(), name=grupo, marker_color=color,
                text=filas["n"].map(lambda n: f"n={n}"),
                textposition="outside", cliponaxis=False,
                customdata=filas[["n", "promedio", "porcentaje"]].to_numpy(),
                hovertemplate=(f"<b>{grupo} · %{{x}}</b>"
                               "<br>Mediana: USD %{y:,.2f}"
                               "<br>Promedio: USD %{customdata[1]:,.2f}"
                               "<br>Registros: %{customdata[0]:,.0f}"
                               "<br>Parte del grupo visible: %{customdata[2]:.1f}%<extra></extra>"),
            )
    fig.update_layout(
        title="Gasto mediano por motivo de viaje (base ficticia, 2022)",
        xaxis_title="Motivo de viaje",
        xaxis=dict(categoryorder="array",
                   categoryarray=["Turismo", "Negocios", "Visita familiar", "Estudios"]),
        yaxis_title="Mediana de Gasto_Total_USD por registro",
        barmode="group", template="plotly_white", height=460,
        margin=dict(l=80, r=55, t=80, b=65))
    return compactar(fig, "Gasto mediano · motivo de viaje", leyenda=True)


def tarjeta(titulo, valor_id):
    return html.Div([
        html.Span(titulo, className="kpi-label"),
        html.Strong(id=valor_id, className="kpi-value"),
    ], className="kpi")


app = Dash(__name__)
server = app.server
app.title = "Viajeros LATAM 2022"
# CSS incorporado: el script sigue siendo un solo archivo junto al Excel.
ESTILOS = """
:root { --noche:#102A43; --aereo:#1769AA; --cielo:#79BDE8;
        --ala:#A6B8C8; --fondo:#ECF4FA; }
* { box-sizing:border-box; }
body { margin:0; background:var(--fondo); color:var(--noche);
       font-family:Arial,Helvetica,sans-serif; }
.dashboard { height:100dvh; min-height:690px; padding:10px 14px; display:grid;
             grid-template-rows:auto auto auto minmax(0,1fr) auto; gap:7px; }
.cabecera { display:flex; align-items:baseline; gap:14px; border-bottom:3px solid var(--cielo); }
.cabecera h1 { font-size:19px; margin:0 0 5px; color:var(--noche); }
.cabecera p { margin:0; font-size:11px; color:#466077; }
.reiniciar { margin-left:auto; flex-shrink:0; border:1px solid var(--aereo);
            background:var(--aereo); color:white; font-weight:bold;
            font-size:11px; border-radius:6px; padding:6px 11px; cursor:pointer; }
.reiniciar:hover,.reiniciar:focus-visible { background:var(--noche); }
.filtros { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:9px; }
.filtro { min-width:0; font-size:11px; font-weight:bold; }
.filtro label { display:block; margin-bottom:2px; }
.filtro .Select-control { min-height:32px; border-color:#AAC4D7; }
.filtro .Select-value-label { color:var(--noche)!important; }
.kpis { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:9px; }
.kpi { padding:7px 10px; background:white; border:1px solid #D7E5EE;
       border-left:3px solid var(--aereo); border-radius:7px; min-width:0; }
.kpi-label { font-size:11px; color:#466077; display:block; }
.kpi-value { font-size:19px; display:block; color:var(--noche); }
.contenido { min-height:0; display:grid; grid-template-rows:auto minmax(0,1fr);
             gap:5px; }
.estado { margin:0; font-size:11px; font-weight:bold; color:var(--aereo); }
.graficas { min-height:0; display:grid; grid-template-columns:repeat(3,minmax(0,1fr));
            grid-template-rows:repeat(2,minmax(0,1fr)); gap:7px; }
.panel { min-height:0; min-width:0; overflow:hidden; background:white;
         border-radius:8px; border:1px solid #D7E5EE; }
.panel .dash-graph { height:100%; }
.evidencia { padding:12px 15px; display:flex; flex-direction:column;
             justify-content:center; gap:8px; }
.evidencia h2 { margin:0; font-size:15px; color:var(--aereo); }
.evidencia .dato { border-left:3px solid var(--cielo); padding-left:8px; }
.evidencia .dato strong { display:block; font-size:17px; line-height:1.15; }
.evidencia .dato span { font-size:11px; color:#466077; }
.evidencia p { margin:1px 0 0; font-size:10px; line-height:1.35; color:#466077; }
.pie { margin:0; font-size:10px; color:#466077; }
@media (max-width:1100px), (max-height:690px) {
 .dashboard { height:auto; min-height:100dvh; }
 .graficas { grid-template-columns:repeat(2,minmax(0,1fr));
             grid-template-rows:none; grid-auto-rows:270px; }
 .filtros { grid-template-columns:repeat(2,minmax(0,1fr)); }
}
@media (max-width:650px) {
 .cabecera { display:block; }
 .reiniciar { margin:5px 0; }
 .filtros,.kpis,.graficas { grid-template-columns:1fr; }
 .graficas { grid-auto-rows:300px; }
}
"""
app.index_string = app.index_string.replace("</head>", "<style>" + ESTILOS + "</style></head>")
app.layout = html.Main([
    html.Header([
        html.H1("Viajeros LATAM 2022"),
        html.P("Base ficticia · 2022 · cada registro representa un viajero"),
        html.Button("Restablecer filtros", id="reiniciar-filtros", n_clicks=0,
                    className="reiniciar", title="Volver a mostrar toda la base"),
    ], className="cabecera"),
    html.Div([
        html.Div([
            html.Label(nombre, htmlFor=f"filtro-{clave}"),
            dcc.Dropdown(
                id=f"filtro-{clave}", multi=True, clearable=True,
                options=[{"label": ETIQUETAS.get(v, v), "value": v}
                         for v in sorted(datos[columna].dropna().unique())],
                value=sorted(datos[columna].dropna().unique()),
            ),
        ], className="filtro")
        for clave, (columna, nombre) in CAMPOS.items()
    ], className="filtros"),
    html.Div([
        tarjeta("Registros visibles", "total-registros"),
        tarjeta("Países visibles", "total-paises"),
        tarjeta("Promedio USD / registro", "gasto-promedio"),
        tarjeta("Mediana USD / registro", "gasto-mediano"),
    ], className="kpis"),
    html.Div([
        html.P(id="estado-filtros", role="status", className="estado"),
        html.Div([
            html.Div(dcc.Graph(id="grafico-paises", responsive=True,
                               config={"displayModeBar": False}), className="panel"),
            html.Div(dcc.Graph(id="grafico-gasto-paises", responsive=True,
                               config={"displayModeBar": False}), className="panel"),
            html.Div(dcc.Graph(id="grafico-tipo-vuelo", responsive=True,
                               config={"displayModeBar": False}), className="panel"),
            html.Div(dcc.Graph(id="grafico-clase", responsive=True,
                               config={"displayModeBar": False}), className="panel"),
            html.Div(dcc.Graph(id="grafico-motivo", responsive=True,
                               config={"displayModeBar": False}), className="panel"),
            html.Aside([
                html.H2("Evidencia del cuaderno · 2.500 registros"),
                html.Div([html.Strong("p = 0,000612"),
                          html.Span("Welch: media Colombia frente a los otros seis países")],
                         className="dato"),
                html.Div([html.Strong("R² prueba = 0,4517"),
                          html.Span("Regresión lineal múltiple · sección 15")],
                         className="dato"),
                html.Div([html.Strong("74,8 % → 84,4 %"),
                          html.Span("Exactitud logística: gasto solo → modelo ampliado")],
                         className="dato"),
                html.P("Métricas fijas de los modelos originales: no cambian al filtrar. "
                       "Base ficticia; no representan ni predicen la población real."),
            ], className="panel evidencia"),
        ], className="graficas"),
    ], className="contenido"),
    html.P("Datos ficticios · Colombia: azul; demás países: gris · Pase el cursor para ver n y gasto · Los filtros se combinan.",
           className="pie"),
], className="dashboard")


@app.callback(
    Output("total-registros", "children"), Output("total-paises", "children"),
    Output("gasto-promedio", "children"), Output("gasto-mediano", "children"),
    Output("estado-filtros", "children"), Output("grafico-paises", "figure"),
    Output("grafico-gasto-paises", "figure"),
    Output("grafico-tipo-vuelo", "figure"),
    Output("grafico-clase", "figure"),
    Output("grafico-motivo", "figure"),
    *(Input(f"filtro-{clave}", "value") for clave in CAMPOS),
)
def actualizar(pais, motivo, vuelo, clase):
    seleccion = dict(zip(CAMPOS, (pais, motivo, vuelo, clase)))
    vista = filtrar(datos, seleccion)
    n, paises, promedio, mediana = indicadores(vista)
    dinero = lambda valor: f"{valor:,.2f}" if valor is not None else "Sin datos"
    return (f"{n:,}", str(paises), dinero(promedio), dinero(mediana),
            f"Selección actual: {n:,} registros."
            if n else "No hay registros para esta combinación de filtros.",
            grafico_paises(vista), grafico_gasto_paises(vista),
            grafico_tipo_vuelo(vista), grafico_clase(vista),
            grafico_motivo(vista))


@app.callback(
    *(Output(f"filtro-{clave}", "value") for clave in CAMPOS),
    Input("reiniciar-filtros", "n_clicks"),
    prevent_initial_call=True,
)
def restablecer_filtros(_clics):
    """Un clic vuelve a marcar todas las opciones de los cuatro filtros."""
    return tuple(sorted(datos[columna].dropna().unique().tolist())
                 for columna, _nombre in CAMPOS.values())


if __name__ == "__main__":
    # Binder asigna un puerto al servidor proxy; localmente se mantiene 8050.
    app.run(debug=False, host="127.0.0.1", port=int(os.environ.get("PORT", "8050")))
