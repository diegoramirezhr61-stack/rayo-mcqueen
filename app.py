"""
⚡ RAYO McQUEEN — Asistente Virtual de Estadística Aplicada
Universidad Mariano Gálvez de Guatemala · Facultad de Ingeniería · Física II
Ejecutar con:  streamlit run app.py
"""
import random

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

import motor as m

# ═════════════════════════ DATOS DEL EQUIPO (edita aquí) ═════════════════════════
INTEGRANTES = ["Marck Anthony Chanchavac Bay", "Helen Mishell Buc Lorenzo "]
ASIGNATURA = "Física II"
SECCION = "A"
CODIGO_CURSO = "22026-2990-020-A"
UNIVERSIDAD = "Universidad Mariano Gálvez de Guatemala"
# ═══════════════════════════════════════════════════════════════════════════════

# Colores de los personajes de Cars
ROJO = "#C8102E"       # Rayo McQueen
AMARILLO = "#FFD100"   # rayo / Cruz Ramírez
AZUL = "#1B3A6B"       # Doc Hudson
CIELO = "#4FA3D9"      # Sally
HERRUMBRE = "#8B5A2B"  # Mate
NEGRO = "#14181F"      # Jackson Storm
CREMA = "#FFF8E7"

st.set_page_config(page_title="Rayo McQueen · Estadística Aplicada", page_icon="⚡", layout="wide")

st.markdown(f"""
<style>
.stApp {{ background: {CREMA}; }}
[data-testid="stSidebar"] {{ background: linear-gradient(180deg, {AZUL} 0%, {NEGRO} 100%); }}
[data-testid="stSidebar"] * {{ color: #ffffff !important; }}
.bandera {{ height: 16px; border-radius: 6px; margin: 6px 0 14px 0;
  background: repeating-conic-gradient({NEGRO} 0% 25%, #ffffff 0% 50%) 0 0 / 32px 32px; }}
.cabecera {{ background: linear-gradient(135deg, {ROJO} 0%, #8E0B20 100%); border-radius: 16px;
  padding: 18px 24px; border-bottom: 6px solid {AMARILLO}; box-shadow: 0 4px 14px rgba(0,0,0,.25); }}
.cabecera h1 {{ color: #fff; margin: 0; font-size: 2.1rem; letter-spacing: .5px; }}
.cabecera .rayo {{ color: {AMARILLO}; }}
.cabecera p {{ color: {AMARILLO}; margin: 4px 0 0 0; font-weight: 600; }}
.cabecera .equipo {{ color: #fff; font-weight: 400; font-size: .9rem; margin-top: 8px; opacity: .95; }}
h2, h3 {{ color: {AZUL}; }}
.tarjeta {{ background: #fff; border-left: 8px solid {ROJO}; border-radius: 10px; padding: 12px 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,.12); margin-bottom: 10px; }}
.tarjeta b {{ color: {ROJO}; }}
div.stButton > button {{ background: {ROJO}; color: #fff; border: 2px solid {AMARILLO};
  border-radius: 10px; font-weight: 700; }}
div.stButton > button:hover {{ background: {AMARILLO}; color: {NEGRO}; border-color: {ROJO}; }}
[data-testid="stMetric"] {{ background: #fff; border-top: 5px solid {AMARILLO}; border-radius: 10px;
  padding: 8px 12px; box-shadow: 0 2px 6px rgba(0,0,0,.1); }}
.pie {{ text-align: center; color: {AZUL}; font-size: .85rem; margin-top: 24px; }}
</style>
""", unsafe_allow_html=True)


# ═════════════════════════ Utilidades de interfaz ═════════════════════════

def cabecera():
    st.markdown(f"""
<div class="cabecera">
  <h1><span class="rayo">⚡</span> RAYO McQUEEN · Asistente de Estadística Aplicada</h1>
  <p>Velocidad, precisión y ¡Ka-chow! en cada cálculo 🏁</p>
  <div class="equipo">👥 {' &nbsp;·&nbsp; '.join(INTEGRANTES)} &nbsp;|&nbsp; 📘 {ASIGNATURA} · Sección {SECCION} ({CODIGO_CURSO}) &nbsp;|&nbsp; 🎓 {UNIVERSIDAD}</div>
</div>
<div class="bandera"></div>
""", unsafe_allow_html=True)


def mate(msg):
    st.warning(f"🛻 **Mate dice:** {msg}")


def rayo(msg):
    st.success(f"⚡ **Rayo:** {msg}")


def tarjeta(html):
    st.markdown(f'<div class="tarjeta">{html}</div>', unsafe_allow_html=True)


def leer_datos(texto):
    datos, err = m.parse_numbers(texto)
    if err:
        mate(err)
        return None
    return datos


def figura(w=7, h=3.8):
    fig, ax = plt.subplots(figsize=(w, h))
    fig.patch.set_facecolor(CREMA)
    ax.set_facecolor("#ffffff")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.grid(alpha=.25)
    return fig, ax


def mostrar(fig):
    st.pyplot(fig)
    plt.close(fig)


# ═════════════════════════ Bloques de resolución (reutilizables) ═════════════════════════

def render_desc(d, unidad=""):
    r = m.descriptiva(d)
    n, u = r["n"], (f" {unidad}" if unidad else "")
    if n < 2:
        mate("Solo hay 1 dato: la desviación estándar muestral no se puede calcular (se necesitan al menos 2).")
    c = st.columns(4)
    c[0].metric("n (datos)", n)
    c[1].metric("Media x̄", m.fmt(r["media"]) + u)
    c[2].metric("Mediana", m.fmt(r["mediana"]) + u)
    c[3].metric("Desv. est. muestral s", (m.fmt(r["s"]) + u) if r["s"] is not None else "—")

    with st.expander("1️⃣ Media aritmética", expanded=True):
        st.latex(r"\bar{x}=\frac{\sum x_i}{n}")
        st.latex(rf"\bar{{x}}=\frac{{{m.suma_latex(d)}}}{{{n}}}=\frac{{{m.fmt(r['suma'])}}}{{{n}}}={m.fmt(r['media'])}\ \text{{{unidad}}}")
    with st.expander("2️⃣ Mediana"):
        st.write("Datos ordenados:", ", ".join(m.fmt(x) for x in r["orden"]))
        if n % 2 == 1:
            pos = (n + 1) // 2
            st.latex(rf"\text{{n impar: posición }}\frac{{n+1}}{{2}}=\frac{{{n}+1}}{{2}}={pos}\Rightarrow \text{{Mediana}}={m.fmt(r['mediana'])}")
        else:
            p1, p2 = n // 2, n // 2 + 1
            st.latex(rf"\text{{n par: promedio de las posiciones }}{p1}\text{{ y }}{p2}:\ \frac{{{m.fmt(r['orden'][p1 - 1])}+{m.fmt(r['orden'][p2 - 1])}}}{{2}}={m.fmt(r['mediana'])}")
    with st.expander("3️⃣ Moda"):
        if r["modas"]:
            tipo = "unimodal" if len(r["modas"]) == 1 else ("bimodal" if len(r["modas"]) == 2 else "multimodal")
            st.write(f"Moda ({tipo}): **{', '.join(m.fmt(x) for x in r['modas'])}** — se repite {r['frec_moda']} veces.")
        else:
            st.write("**No hay moda** (amodal): ningún valor se repite.")
    with st.expander("4️⃣ Rango"):
        st.latex(rf"R=x_{{máx}}-x_{{mín}}={m.fmt(r['maximo'])}-{m.fmt(r['minimo'])}={m.fmt(r['rango'])}")
    with st.expander("5️⃣ Varianza y desviación estándar", expanded=True):
        if n <= 15:
            st.dataframe(m.tabla_desviaciones(d, r["media"]).round(4), hide_index=True)
        st.latex(rf"\sum (x_i-\bar{{x}})^2={m.fmt(r['ss'], 5)}")
        if r["s"] is not None:
            st.markdown("**Muestral** (datos que son una muestra, divide entre n − 1):")
            st.latex(rf"s^2=\frac{{\sum (x_i-\bar{{x}})^2}}{{n-1}}=\frac{{{m.fmt(r['ss'], 5)}}}{{{n - 1}}}={m.fmt(r['var_m'], 5)}\quad\Rightarrow\quad s=\sqrt{{{m.fmt(r['var_m'], 5)}}}={m.fmt(r['s'])}")
        st.markdown("**Poblacional** (si tienes TODA la población, divide entre n):")
        st.latex(rf"\sigma^2=\frac{{\sum (x_i-\bar{{x}})^2}}{{n}}=\frac{{{m.fmt(r['ss'], 5)}}}{{{n}}}={m.fmt(r['var_p'], 5)}\quad\Rightarrow\quad \sigma={m.fmt(r['sigma'])}")
    with st.expander("6️⃣ Otras medidas de dispersión"):
        if r["cv"] is not None:
            st.latex(rf"CV=\frac{{s}}{{|\bar{{x}}|}}\cdot 100\%=\frac{{{m.fmt(r['s'])}}}{{{m.fmt(abs(r['media']))}}}\cdot 100={m.fmt(r['cv'], 2)}\%")
        st.write(f"Q1 = {m.fmt(r['q1'])} · Q3 = {m.fmt(r['q3'])} · Rango intercuartílico (IQR) = {m.fmt(r['iqr'])}")
    st.info("🧠 **Interpretación:** " + m.interpretar_dispersion(r, unidad))
    return r


def render_exp(d, magnitud, unidad, destino=None, referencia=None):
    res = m.medicion(d)
    if res is None:
        mate("Con una sola medición no se puede estimar la incertidumbre. Ingresa al menos 2.")
        return
    r, n = res["r"], len(d)
    st.markdown(f"**Magnitud:** {magnitud} · **Unidad:** {unidad} · **n = {n}**")
    st.latex(rf"\bar{{x}}=\frac{{{m.suma_latex(d)}}}{{{n}}}={m.fmt(r['media'])}\ \text{{{unidad}}}")
    st.latex(rf"s=\sqrt{{\frac{{\sum (x_i-\bar{{x}})^2}}{{n-1}}}}=\sqrt{{\frac{{{m.fmt(r['ss'], 5)}}}{{{n - 1}}}}}={m.fmt(r['s'])}\ \text{{{unidad}}}")
    st.latex(rf"u(\bar{{x}})=\frac{{s}}{{\sqrt{{n}}}}=\frac{{{m.fmt(r['s'])}}}{{\sqrt{{{n}}}}}={m.fmt(res['u'])}\ \text{{{unidad}}}")
    final = f"{m.fmt_dec(res['media_r'], res['dec'])} ± {m.fmt_dec(res['u_r'], res['dec'])} {unidad}"
    rayo(f"Resultado: **x̄ = {final}**" + (f" (incertidumbre relativa {m.fmt(res['rel'], 2)} %)" if res["rel"] is not None else ""))
    if destino and destino != unidad:
        v = m.convertir(res["media_r"], magnitud, unidad, destino)
        uu = m.convertir(res["u_r"], magnitud, unidad, destino)
        f1, f2 = m.UNIDADES[magnitud][unidad], m.UNIDADES[magnitud][destino]
        st.latex(rf"1\ \text{{{unidad}}}={m.fmt(f1 / f2, 8)}\ \text{{{destino}}}\ \Rightarrow\ {m.fmt(res['media_r'])}\cdot {m.fmt(f1 / f2, 8)}={m.fmt(v, 8)}\ \text{{{destino}}}")
        rayo(f"En {destino}: **{m.fmt(v, 8)} ± {m.fmt(uu, 8)} {destino}**")
    if referencia is not None and referencia != 0:
        err = abs(r["media"] - referencia) / abs(referencia) * 100
        st.latex(rf"E\%=\frac{{|\bar{{x}}-x_{{ref}}|}}{{|x_{{ref}}|}}\cdot 100=\frac{{|{m.fmt(r['media'])}-{m.fmt(referencia)}|}}{{{m.fmt(abs(referencia))}}}\cdot 100={m.fmt(err, 3)}\%")
    st.info("🧠 **Interpretación:** " + m.interpretar_dispersion(r, unidad))


def render_freq(d, k=None, titulo_x="Valores"):
    df, edges, k, ancho = m.tabla_frecuencias(d, k)
    n = len(d)
    st.latex(rf"k\approx 1+\log_2(n)={m.sturges(n)}\ (\text{{Sturges}})\qquad A=\frac{{R}}{{k}}=\frac{{{m.fmt(max(d) - min(d))}}}{{{k}}}={m.fmt(ancho, 4)}")
    st.dataframe(df, hide_index=True)
    fig, ax = figura()
    ax.hist(d, bins=edges, color=ROJO, edgecolor=AMARILLO, linewidth=2)
    ax.set_xlabel(titulo_x)
    ax.set_ylabel("Frecuencia (f)")
    ax.set_title("Histograma", color=AZUL, fontweight="bold")
    mostrar(fig)


def render_clasica(fav, tot):
    st.latex(rf"P(A)=\frac{{\text{{casos favorables}}}}{{\text{{casos posibles}}}}=\frac{{{fav}}}{{{tot}}}={m.fmt(fav / tot, 4)}")
    rayo(f"P = **{m.fmt(fav / tot, 4)}** ({m.fmt(fav / tot * 100, 2)} %). Probabilidad del complemento: {m.fmt(1 - fav / tot, 4)}.")


def render_union(pa, pb, pab):
    pu = pa + pb - pab
    st.latex(rf"P(A\cup B)=P(A)+P(B)-P(A\cap B)={m.fmt(pa)}+{m.fmt(pb)}-{m.fmt(pab)}={m.fmt(pu)}")
    prod = pa * pb
    ind = abs(prod - pab) < 1e-9
    signo = "=" if ind else r"\neq"
    st.latex(rf"P(A)\cdot P(B)={m.fmt(pa)}\cdot {m.fmt(pb)}={m.fmt(prod)}\ \ {signo}\ \ P(A\cap B)={m.fmt(pab)}")
    rayo(f"P(A∪B) = **{m.fmt(pu)}**. Los eventos {'**son independientes**' if ind else '**NO son independientes**'}.")
    if pb > 0:
        st.latex(rf"P(A|B)=\frac{{P(A\cap B)}}{{P(B)}}=\frac{{{m.fmt(pab)}}}{{{m.fmt(pb)}}}={m.fmt(pab / pb)}")


def render_binom(n, p, k):
    pk = m.binom_pmf(n, p, k)
    st.latex(rf"P(X={k})=\binom{{{n}}}{{{k}}}\,p^{{{k}}}(1-p)^{{{n - k}}}=\binom{{{n}}}{{{k}}}({m.fmt(p)})^{{{k}}}({m.fmt(1 - p)})^{{{n - k}}}={m.fmt(pk, 5)}")
    rayo(f"P(X = {k}) = **{m.fmt(pk, 5)}** ({m.fmt(pk * 100, 3)} %). Media = np = {m.fmt(n * p)}; σ = √(npq) = {m.fmt((n * p * (1 - p)) ** .5)}.")
    xs = list(range(n + 1))
    fig, ax = figura(6, 3.2)
    ax.bar(xs, [m.binom_pmf(n, p, i) for i in xs], color=[ROJO if i == k else CIELO for i in xs], edgecolor=AZUL)
    ax.set_xlabel("k (éxitos)")
    ax.set_ylabel("P(X = k)")
    ax.set_xticks(xs)
    mostrar(fig)


def render_normal(mu, sigma, modo, a, b=None):
    fig, ax = figura(7, 3.6)
    xs = np.linspace(mu - 4 * sigma, mu + 4 * sigma, 400)
    ax.plot(xs, [m.norm_pdf(x, mu, sigma) for x in xs], color=AZUL, lw=2)
    if modo == "menor":
        z = (a - mu) / sigma
        pr = m.norm_cdf(z)
        st.latex(rf"z=\frac{{x-\mu}}{{\sigma}}=\frac{{{m.fmt(a)}-{m.fmt(mu)}}}{{{m.fmt(sigma)}}}={m.fmt(z, 4)}")
        st.latex(rf"P(X<{m.fmt(a)})=\Phi({m.fmt(z, 4)})={m.fmt(pr, 5)}")
        mask = xs <= a
        etiqueta = f"P(X < {m.fmt(a)})"
    elif modo == "mayor":
        z = (a - mu) / sigma
        pr = 1 - m.norm_cdf(z)
        st.latex(rf"z=\frac{{{m.fmt(a)}-{m.fmt(mu)}}}{{{m.fmt(sigma)}}}={m.fmt(z, 4)}")
        st.latex(rf"P(X>{m.fmt(a)})=1-\Phi({m.fmt(z, 4)})=1-{m.fmt(m.norm_cdf(z), 5)}={m.fmt(pr, 5)}")
        mask = xs >= a
        etiqueta = f"P(X > {m.fmt(a)})"
    else:
        z1, z2 = (a - mu) / sigma, (b - mu) / sigma
        pr = m.norm_cdf(z2) - m.norm_cdf(z1)
        st.latex(rf"z_1=\frac{{{m.fmt(a)}-{m.fmt(mu)}}}{{{m.fmt(sigma)}}}={m.fmt(z1, 4)}\qquad z_2=\frac{{{m.fmt(b)}-{m.fmt(mu)}}}{{{m.fmt(sigma)}}}={m.fmt(z2, 4)}")
        st.latex(rf"P({m.fmt(a)}<X<{m.fmt(b)})=\Phi({m.fmt(z2, 4)})-\Phi({m.fmt(z1, 4)})={m.fmt(m.norm_cdf(z2), 5)}-{m.fmt(m.norm_cdf(z1), 5)}={m.fmt(pr, 5)}")
        mask = (xs >= a) & (xs <= b)
        etiqueta = f"P({m.fmt(a)} < X < {m.fmt(b)})"
    ys = np.array([m.norm_pdf(x, mu, sigma) for x in xs])
    ax.fill_between(xs, ys, where=mask, color=ROJO, alpha=.55, label=f"{etiqueta} = {m.fmt(pr, 4)}")
    ax.axvline(mu, color=AMARILLO, lw=2, ls="--", label=f"μ = {m.fmt(mu)}")
    ax.legend()
    ax.set_xlabel("x")
    ax.set_ylabel("f(x)")
    mostrar(fig)
    rayo(f"{etiqueta} = **{m.fmt(pr, 5)}** ({m.fmt(pr * 100, 2)} %)")
    return pr


def render_reg(x, y, nx="x", ny="y", x_pred=None):
    try:
        rg = m.regresion(x, y)
    except ValueError as e:
        mate(str(e))
        return
    if len(x) <= 12:
        st.dataframe(m.tabla_regresion(x, y, rg).round(5), hide_index=True)
    st.latex(rf"\bar{{x}}={m.fmt(rg['mx'])},\ \bar{{y}}={m.fmt(rg['my'])},\ S_{{xx}}={m.fmt(rg['sxx'], 5)},\ S_{{yy}}={m.fmt(rg['syy'], 5)},\ S_{{xy}}={m.fmt(rg['sxy'], 5)}")
    st.latex(rf"b=\frac{{S_{{xy}}}}{{S_{{xx}}}}=\frac{{{m.fmt(rg['sxy'], 5)}}}{{{m.fmt(rg['sxx'], 5)}}}={m.fmt(rg['b'], 5)}\qquad a=\bar{{y}}-b\bar{{x}}={m.fmt(rg['my'])}-({m.fmt(rg['b'], 5)})({m.fmt(rg['mx'])})={m.fmt(rg['a'], 5)}")
    signo = "+" if rg["a"] >= 0 else "-"
    rayo(f"Recta de regresión: **ŷ = {m.fmt(rg['b'], 4)}·x {signo} {m.fmt(abs(rg['a']), 4)}**")
    if rg["r"] is not None:
        st.latex(rf"r=\frac{{S_{{xy}}}}{{\sqrt{{S_{{xx}}S_{{yy}}}}}}=\frac{{{m.fmt(rg['sxy'], 5)}}}{{\sqrt{{({m.fmt(rg['sxx'], 5)})({m.fmt(rg['syy'], 5)})}}}}={m.fmt(rg['r'], 5)}\qquad r^2={m.fmt(rg['r2'], 5)}")
    st.info("🧠 **Interpretación:** " + m.interpretar_r(rg["r"]))
    if x_pred is not None:
        yp = rg["a"] + rg["b"] * x_pred
        st.latex(rf"\hat{{y}}({m.fmt(x_pred)})={m.fmt(rg['a'], 5)}+{m.fmt(rg['b'], 5)}\cdot {m.fmt(x_pred)}={m.fmt(yp, 5)}")
        if x_pred < min(x) or x_pred > max(x):
            mate("Ese valor está fuera del rango de tus datos (extrapolación): la predicción es poco confiable.")
    fig, ax = figura()
    ax.scatter(x, y, s=70, color=ROJO, edgecolor=AMARILLO, linewidth=1.5, zorder=3, label="Datos")
    xx = np.linspace(min(x), max(x), 50)
    ax.plot(xx, rg["a"] + rg["b"] * xx, color=AZUL, lw=2.5, label="Recta ajustada")
    if x_pred is not None:
        ax.scatter([x_pred], [rg["a"] + rg["b"] * x_pred], marker="*", s=220, color=AMARILLO, edgecolor=NEGRO, zorder=4, label="Predicción")
    ax.set_xlabel(nx)
    ax.set_ylabel(ny)
    ax.set_title("Diagrama de dispersión", color=AZUL, fontweight="bold")
    ax.legend()
    mostrar(fig)


def render_popsam(d):
    r = m.descriptiva(d)
    n = r["n"]
    if n < 2:
        mate("Necesitas al menos 2 datos para comparar σ y s.")
        return
    c = st.columns(3)
    c[0].metric("σ (poblacional, ÷ n)", m.fmt(r["sigma"]))
    c[1].metric("s (muestral, ÷ n−1)", m.fmt(r["s"]))
    c[2].metric("Factor √(n/(n−1))", m.fmt((n / (n - 1)) ** .5))
    st.latex(rf"\sigma=\sqrt{{\frac{{{m.fmt(r['ss'], 5)}}}{{{n}}}}}={m.fmt(r['sigma'])}\qquad s=\sqrt{{\frac{{{m.fmt(r['ss'], 5)}}}{{{n - 1}}}}}={m.fmt(r['s'])}")
    st.info(f"🧠 **Interpretación:** s resulta {m.fmt((r['s'] / r['sigma'] - 1) * 100, 2)} % mayor que σ con n = {n}. "
            "Al dividir entre n − 1 (corrección de Bessel) se compensa que una muestra tiende a subestimar la dispersión real de la población. "
            "Con n grande la diferencia casi desaparece.")


# ═════════════════════════ Páginas ═════════════════════════

def pagina_inicio():
    st.subheader("🏁 Línea de salida")
    tarjeta("¡Hola! Soy <b>Rayo McQueen</b> y te ayudo a resolver problemas de <b>estadística aplicada a la Física</b>: "
            "calculo, muestro la <b>fórmula</b>, la <b>sustitución</b>, el <b>procedimiento</b> y la <b>respuesta final</b>, "
            "y te explico qué significan los resultados.")
    cols = st.columns(3)
    modulos = [("📊 Estadística descriptiva", "Media, mediana, moda, rango, varianza y desviación estándar."),
               ("🔬 Datos experimentales", "Series de mediciones, unidades, incertidumbre y conversiones."),
               ("📋 Tablas y gráficas", "Tablas de frecuencias, histogramas y diagramas de dispersión."),
               ("🎲 Probabilidad", "Ejercicios básicos, binomial y distribución normal."),
               ("📈 Correlación y regresión", "Coeficiente r y recta de mínimos cuadrados."),
               ("🧠 Interpretación", "Diferencia entre σ poblacional y s muestral, y cómo leer resultados.")]
    for i, (t, dsc) in enumerate(modulos):
        with cols[i % 3]:
            tarjeta(f"<b>{t}</b><br>{dsc}")
    tarjeta("💬 <b>Pregúntale a Rayo</b>: escribe tu duda con datos (ej. <i>«media y desviación de 2.1, 2.3, 2.2, 2.4, 2.0»</i>). "
            "📚 <b>Garaje de Doc</b>: 12 ejemplos resueltos. 🏆 <b>Entrenamiento con Cruz</b>: práctica con retroalimentación.")
    st.markdown("**Cómo ingresar datos:** sepáralos con comas o espacios (`2.1, 2.3, 2.2`). "
                "Si usas coma decimal, sepáralos con punto y coma (`2,1; 2,3; 2,2`).")
    if st.button("⚡ Probar el ejemplo del ingeniero (corriente en A)"):
        e = m.EJEMPLOS[0]
        st.markdown(f"**{e['enunciado']}**")
        render_exp(e["datos"], e["magnitud"], e["unidad"])


def pagina_descriptiva():
    st.subheader("📊 Estadística descriptiva · Pista de Radiator Springs")
    c1, c2 = st.columns([3, 1])
    texto = c1.text_area("Datos (separados por comas)", "2.1, 2.3, 2.2, 2.4, 2.0", key="desc_datos", height=100)
    unidad = c2.text_input("Unidad (opcional)", "A", key="desc_u")
    d = leer_datos(texto)
    if d:
        render_desc(d, unidad.strip())


def pagina_experimental():
    st.subheader("🔬 Datos experimentales · Taller de Luigi y Guido")
    c = st.columns(3)
    magnitud = c[0].selectbox("Magnitud física", list(m.UNIDADES), key="exp_mag")
    unidades = list(m.UNIDADES[magnitud])
    unidad = c[1].selectbox("Unidad de tus mediciones", unidades, key=f"exp_u_{magnitud}")
    destino = c[2].selectbox("Convertir resultado a", unidades, index=0, key=f"exp_d_{magnitud}")
    texto = st.text_area("Mediciones", "2.1, 2.3, 2.2, 2.4, 2.0", key="exp_datos", height=90)
    ref_txt = st.text_input("Valor de referencia (opcional, para el % de error)", "", key="exp_ref")
    d = leer_datos(texto)
    ref = None
    if ref_txt.strip():
        v, err = m.parse_numbers(ref_txt)
        if err or len(v) != 1:
            mate("El valor de referencia debe ser un solo número.")
        else:
            ref = v[0]
    if d:
        render_exp(d, magnitud, unidad, destino, ref)


def pagina_tablas():
    st.subheader("📋 Tablas y gráficas · Pista de Radiator Springs")
    t1, t2 = st.tabs(["Tabla de frecuencias e histograma", "Diagrama de dispersión"])
    with t1:
        texto = st.text_area("Datos", "21, 22, 22, 23, 23, 23, 24, 24, 24, 24, 25, 25, 25, 26, 26, 27, 27, 28, 29, 31", key="tab_datos", height=90)
        k = st.number_input("Número de clases (0 = automático, regla de Sturges)", 0, 30, 0, key="tab_k")
        d = leer_datos(texto)
        if d:
            if len(d) < 2:
                mate("Ingresa al menos 2 datos para construir la tabla.")
            else:
                render_freq(d, int(k) or None)
    with t2:
        cx, cy = st.columns(2)
        tx = cx.text_area("Datos x", "1, 2, 3, 4, 5, 6", key="dis_x", height=80)
        ty = cy.text_area("Datos y", "2.1, 3.9, 6.2, 7.8, 10.1, 12.0", key="dis_y", height=80)
        x, y = leer_datos(tx), leer_datos(ty)
        if x and y:
            if len(x) != len(y):
                mate(f"x tiene {len(x)} datos y y tiene {len(y)}. Deben ser la misma cantidad.")
            else:
                fig, ax = figura()
                ax.scatter(x, y, s=80, color=ROJO, edgecolor=AMARILLO, linewidth=1.5)
                ax.set_xlabel("x")
                ax.set_ylabel("y")
                ax.set_title("Diagrama de dispersión", color=AZUL, fontweight="bold")
                mostrar(fig)


def pagina_probabilidad():
    st.subheader("🎲 Probabilidad · Copa Pistón")
    t1, t2, t3, t4 = st.tabs(["Clásica", "Unión / independencia", "Binomial", "Normal"])
    with t1:
        c = st.columns(2)
        fav = c[0].number_input("Casos favorables", 0, 100000, 3, key="p_fav")
        tot = c[1].number_input("Casos posibles", 0, 100000, 6, key="p_tot")
        if tot == 0:
            mate("Los casos posibles deben ser mayores que 0.")
        elif fav > tot:
            mate("Los casos favorables no pueden ser más que los posibles.")
        else:
            render_clasica(int(fav), int(tot))
    with t2:
        c = st.columns(3)
        pa = c[0].number_input("P(A)", 0.0, 1.0, 0.40, 0.01, key="u_pa")
        pb = c[1].number_input("P(B)", 0.0, 1.0, 0.50, 0.01, key="u_pb")
        pab = c[2].number_input("P(A∩B)", 0.0, 1.0, 0.20, 0.01, key="u_pab")
        if pab > min(pa, pb) + 1e-12:
            mate("P(A∩B) no puede ser mayor que P(A) ni que P(B). Revisa los datos.")
        elif pa + pb - pab > 1 + 1e-12:
            mate("Con esos valores P(A∪B) supera 1. Revisa los datos.")
        else:
            render_union(pa, pb, pab)
    with t3:
        c = st.columns(3)
        n = c[0].number_input("n (ensayos)", 1, 200, 5, key="b_n")
        p = c[1].number_input("p (éxito)", 0.0, 1.0, 0.5, 0.01, key="b_p")
        k = c[2].number_input("k (éxitos)", 0, 200, 3, key="b_k")
        if k > n:
            mate("k no puede ser mayor que n.")
        else:
            render_binom(int(n), p, int(k))
    with t4:
        c = st.columns(3)
        mu = c[0].number_input("Media μ", value=70.0, key="n_mu")
        sg = c[1].number_input("Desviación σ", value=10.0, key="n_sg")
        modo_t = c[2].selectbox("Probabilidad", ["P(X < a)", "P(X > a)", "P(a < X < b)", "Valor de x para un percentil"], key="n_modo")
        if sg <= 0:
            mate("La desviación estándar σ debe ser mayor que 0.")
        elif modo_t.startswith("Valor"):
            pc = st.number_input("Percentil (%)", 0.1, 99.9, 90.0, key="n_pc")
            z = m.norm_ppf(pc / 100)
            x = mu + z * sg
            st.latex(rf"z=\Phi^{{-1}}({m.fmt(pc / 100)})={m.fmt(z, 4)}\qquad x=\mu+z\sigma={m.fmt(mu)}+({m.fmt(z, 4)})({m.fmt(sg)})={m.fmt(x, 4)}")
            rayo(f"El percentil {m.fmt(pc)} corresponde a x = **{m.fmt(x, 4)}**")
        elif modo_t == "P(a < X < b)":
            cc = st.columns(2)
            a = cc[0].number_input("a", value=60.0, key="n_a")
            b = cc[1].number_input("b", value=85.0, key="n_b")
            if a >= b:
                mate("Debe cumplirse a < b.")
            else:
                render_normal(mu, sg, "entre", a, b)
        else:
            a = st.number_input("a", value=85.0, key="n_a1")
            render_normal(mu, sg, "menor" if modo_t == "P(X < a)" else "mayor", a)


def pagina_regresion():
    st.subheader("📈 Correlación y regresión lineal · Ruta 66")
    cx, cy = st.columns(2)
    tx = cx.text_area("Datos x", "0.02, 0.04, 0.06, 0.08, 0.10", key="r_x", height=80)
    ty = cy.text_area("Datos y", "0.9, 2.1, 2.9, 4.1, 5.0", key="r_y", height=80)
    nx = cx.text_input("Nombre de x", "x", key="r_nx")
    ny = cy.text_input("Nombre de y", "y", key="r_ny")
    pred_txt = st.text_input("Predecir y para x = (opcional)", "", key="r_pred")
    x, y = leer_datos(tx), leer_datos(ty)
    pred = None
    if pred_txt.strip():
        v, err = m.parse_numbers(pred_txt)
        if err or len(v) != 1:
            mate("El valor para predecir debe ser un solo número.")
        else:
            pred = v[0]
    if x and y:
        render_reg(x, y, nx or "x", ny or "y", pred)


def pagina_interpretacion():
    st.subheader("🧠 Interpretación · Consejos de Doc Hudson")
    tarjeta("<b>Poblacional (σ)</b>: úsala cuando tienes <b>todos</b> los datos de la población. Divide entre <b>n</b>.<br>"
            "<b>Muestral (s)</b>: úsala cuando tus datos son una <b>muestra</b> (casi siempre en experimentos de laboratorio). Divide entre <b>n − 1</b>.")
    st.latex(r"\sigma=\sqrt{\frac{\sum (x_i-\mu)^2}{N}}\qquad s=\sqrt{\frac{\sum (x_i-\bar{x})^2}{n-1}}")
    texto = st.text_area("Prueba con tus datos", "4, 8, 6, 5, 7", key="int_datos", height=80)
    d = leer_datos(texto)
    if d:
        render_popsam(d)
    st.markdown("**Guía rápida para leer resultados**")
    st.markdown("- **CV < 10 %**: mediciones muy consistentes. **10–20 %**: variación moderada. **> 20 %**: poca consistencia.\n"
                "- **|r| ≥ 0.9** correlación muy fuerte · **0.7–0.9** fuerte · **0.4–0.7** moderada · **< 0.4** débil.\n"
                "- Una probabilidad cercana a 0 es un evento raro; cercana a 1, casi seguro.\n"
                "- Una incertidumbre pequeña frente a la media indica una medición precisa.")


def render_ejemplo(e):
    t = e["tipo"]
    if t == "exp":
        render_exp(e["datos"], e["magnitud"], e["unidad"], e.get("destino"))
    elif t == "desc":
        render_desc(e["datos"], e.get("unidad", ""))
    elif t == "freq":
        render_freq(e["datos"], e.get("k"))
    elif t == "clasica":
        render_clasica(e["fav"], e["tot"])
    elif t == "union":
        render_union(e["pa"], e["pb"], e["pab"])
    elif t == "binom":
        render_binom(e["n"], e["p"], e["k"])
    elif t == "normal":
        render_normal(e["mu"], e["sigma"], e["modo"], e["a"], e["b"])
    elif t == "reg":
        render_reg(e["x"], e["y"], e["nx"], e["ny"], e.get("x_pred"))
    elif t == "popsam":
        render_popsam(e["datos"])


def pagina_ejemplos():
    st.subheader("📚 Garaje de Doc Hudson · 12 ejemplos resueltos")
    for i, e in enumerate(m.EJEMPLOS, 1):
        with st.expander(f"Ejemplo {i}: {e['titulo']}"):
            st.markdown(f"**Enunciado:** {e['enunciado']}")
            render_ejemplo(e)


def pagina_practica():
    st.subheader("🏆 Entrenamiento con Cruz Ramírez · Práctica con retroalimentación")
    ss = st.session_state
    ss.setdefault("aciertos", 0)
    ss.setdefault("intentos", 0)
    ss.setdefault("contador", 0)
    ss.setdefault("ej", None)
    ss.setdefault("ej_tipo", None)
    ss.setdefault("contado", False)
    nombres = list(m.TIPOS_PRACTICA.values())
    claves = list(m.TIPOS_PRACTICA.keys())
    elegido = st.selectbox("¿Qué quieres practicar?", nombres, key="pr_tipo")
    tipo = claves[nombres.index(elegido)]
    nuevo = st.button("🏁 Nuevo ejercicio", key="pr_nuevo")
    if nuevo or ss.ej is None or ss.ej_tipo != tipo:
        ss.ej = m.generar_ejercicio(tipo, random.Random())
        ss.ej_tipo = tipo
        ss.contado = False
        ss.contador += 1
    ej = ss.ej
    c = st.columns(3)
    c[0].metric("Aciertos", ss.aciertos)
    c[1].metric("Intentos", ss.intentos)
    c[2].metric("Copa Pistón", f"{m.fmt(ss.aciertos / ss.intentos * 100, 0)} %" if ss.intentos else "—")
    tarjeta(f"<b>Problema:</b> {ej['enunciado']}".replace("**", ""))
    resp = st.text_input("Tu respuesta", key=f"pr_resp_{ss.contador}")
    if st.button("✅ Revisar respuesta", key=f"pr_chk_{ss.contador}"):
        val, err = m.parse_respuesta(resp)
        if err:
            mate(err)
        else:
            ok, msg = m.evaluar(ej, val)
            if not ss.contado:
                ss.intentos += 1
                ss.aciertos += 1 if ok else 0
                ss.contado = True
            (rayo if ok else mate)(msg)
    with st.expander("👀 Ver solución paso a paso"):
        t = ej["tipo"]
        if t in ("media", "mediana", "s"):
            render_desc(ej["datos"])
        elif t == "normal":
            render_normal(ej["mu"], ej["sigma"], "menor", ej["x"])
        elif t in ("pendiente", "correlacion"):
            render_reg(ej["x"], ej["y"])
        else:
            render_clasica(ej["fav"], ej["tot"])


def pagina_chat():
    st.subheader("💬 Pregúntale a Rayo")
    st.caption("Escribe tu pregunta con datos. Ejemplos: «mediana de 4, 8, 6, 5, 7» · «x: 1,2,3,4 y: 2.1,3.9,6.2,7.8» · «normal con media 70 y desviación 10, P(X<85)»")
    q = st.text_area("Tu pregunta", "Calcula la media y la desviación estándar de 2.1, 2.3, 2.2, 2.4, 2.0", key="chat_q", height=90)
    if st.button("⚡ Preguntar a Rayo", key="chat_go"):
        res = m.interpretar_pregunta(q)
        t = res["tipo"]
        if t in ("vacio", "error"):
            mate(res["mensaje"])
        elif t == "descriptiva":
            d = res["datos"]
            r = m.descriptiva(d)
            foco = res["foco"]
            respuestas = {
                "media": f"La media es **{m.fmt(r['media'])}**.",
                "mediana": f"La mediana es **{m.fmt(r['mediana'])}**.",
                "moda": ("La moda es **" + ", ".join(m.fmt(x) for x in r["modas"]) + "**.") if r["modas"] else "No hay moda: ningún valor se repite.",
                "rango": f"El rango es **{m.fmt(r['rango'])}**.",
                "varianza": f"La varianza muestral es **{m.fmt(r['var_m'], 5)}**." if r["var_m"] is not None else "Necesito al menos 2 datos para la varianza muestral.",
                "desviacion": f"La desviación estándar muestral es **{m.fmt(r['s'])}** (poblacional: {m.fmt(r['sigma'])})." if r["s"] is not None else "Necesito al menos 2 datos para la desviación muestral.",
            }
            if foco == "frecuencias":
                if len(d) < 2:
                    mate("Necesito al menos 2 datos para la tabla de frecuencias.")
                else:
                    render_freq(d)
            else:
                if foco:
                    rayo(respuestas[foco])
                else:
                    st.info("No detecté qué medida quieres, así que te muestro el análisis completo.")
                st.caption("Te dejo el procedimiento completo:")
                render_desc(d)
        elif t == "regresion":
            render_reg(res["x"], res["y"])
        elif t == "normal":
            render_normal(res["mu"], res["sigma"], res["modo"], res["a"], res["b"])


# ═════════════════════════ Navegación ═════════════════════════

PAGINAS = {
    "🏁 Inicio": pagina_inicio,
    "💬 Pregúntale a Rayo": pagina_chat,
    "📊 Estadística descriptiva": pagina_descriptiva,
    "🔬 Datos experimentales": pagina_experimental,
    "📋 Tablas y gráficas": pagina_tablas,
    "🎲 Probabilidad": pagina_probabilidad,
    "📈 Correlación y regresión": pagina_regresion,
    "🧠 Interpretación": pagina_interpretacion,
    "📚 Ejemplos resueltos": pagina_ejemplos,
    "🏆 Práctica": pagina_practica,
}

with st.sidebar:
    st.markdown("## ⚡ Rayo McQueen")
    st.markdown("*Ka-chow! Elige un módulo:*")
    opcion = st.radio("Módulos", list(PAGINAS), label_visibility="collapsed")
    st.markdown("---")
    st.markdown("**Equipo**")
    for nombre in INTEGRANTES:
        st.markdown(f"- {nombre}")
    st.markdown(f"**{ASIGNATURA}** · Sección {SECCION}")

cabecera()
try:
    PAGINAS[opcion]()
except Exception as exc:  # protección final: nunca mostrar un error técnico al usuario
    mate(f"Algo salió mal con esos datos ({type(exc).__name__}). Revisa que estén completos y en el formato correcto.")

st.markdown(f'<div class="pie">⚡ Rayo McQueen · {ASIGNATURA} · Sección {SECCION} · {UNIVERSIDAD}</div>', unsafe_allow_html=True)
