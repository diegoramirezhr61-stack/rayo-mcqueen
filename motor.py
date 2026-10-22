"""
Motor de cálculo de Rayo McQueen (Asistente Virtual de Estadística Aplicada).
Contiene SOLO funciones de cálculo (sin interfaz), para poder probarlas y explicarlas.
"""
import math
import re
from collections import Counter

import numpy as np
import pandas as pd

# ───────────────────────── Utilidades de formato ─────────────────────────


def fmt(x, nd=4):
    """Formatea un número quitando ceros sobrantes (2.2000 -> 2.2)."""
    if x is None:
        return "—"
    try:
        x = float(x)
    except (TypeError, ValueError):
        return str(x)
    if not math.isfinite(x):
        return str(x)
    s = f"{x:.{nd}f}"
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def _t(x):
    """Número para sumas en LaTeX (negativos entre paréntesis)."""
    s = fmt(x)
    return f"({s})" if x < 0 else s


def suma_latex(valores, max_items=8):
    v = [_t(x) for x in valores]
    if len(v) > max_items:
        v = v[:5] + [r"\ldots"] + v[-2:]
    return " + ".join(v)


# ───────────────────────── Lectura de datos ─────────────────────────


def parse_numbers(texto):
    """
    Convierte un texto en lista de números. Devuelve (lista, mensaje_de_error).
    Separadores: coma, espacio o salto de línea. Si usas coma decimal, separa con ';'.
    """
    t = (texto or "").strip()
    if not t:
        return [], "No ingresaste datos. Escribe tus mediciones separadas por comas."
    if ";" in t:
        tokens = [x.replace(",", ".") for x in re.split(r"[;\s]+", t) if x]
    else:
        tokens = [x for x in re.split(r"[,\s]+", t) if x]
    datos = []
    for tok in tokens:
        try:
            v = float(tok)
        except ValueError:
            return [], f"No pude interpretar «{tok}» como número. Revisa tus datos."
        if not math.isfinite(v):
            return [], f"El valor «{tok}» no es un número válido."
        datos.append(v)
    if not datos:
        return [], "No encontré números en lo que escribiste."
    return datos, None


# ───────────────────────── Estadística descriptiva ─────────────────────────


def descriptiva(d):
    a = np.array(d, dtype=float)
    n = int(a.size)
    suma = float(a.sum())
    media = suma / n
    orden = sorted(d)
    mediana = float(np.median(a))
    cnt = Counter(d)
    mx = max(cnt.values())
    modas = sorted(k for k, v in cnt.items() if v == mx) if mx > 1 else []
    rango = float(a.max() - a.min())
    ss = float(((a - media) ** 2).sum())
    var_m = ss / (n - 1) if n > 1 else None
    var_p = ss / n
    s = math.sqrt(var_m) if var_m is not None else None
    sigma = math.sqrt(var_p)
    cv = (s / abs(media) * 100) if (s is not None and media != 0) else None
    q1, q3 = (float(q) for q in np.percentile(a, [25, 75]))
    return dict(n=n, suma=suma, media=media, orden=orden, mediana=mediana,
                modas=modas, frec_moda=mx, minimo=float(a.min()),
                maximo=float(a.max()), rango=rango, ss=ss, var_m=var_m,
                var_p=var_p, s=s, sigma=sigma, cv=cv, q1=q1, q3=q3, iqr=q3 - q1)


def tabla_desviaciones(d, media):
    return pd.DataFrame({"xᵢ": d, "xᵢ − x̄": [x - media for x in d],
                         "(xᵢ − x̄)²": [(x - media) ** 2 for x in d]})


def interpretar_dispersion(r, unidad=""):
    u = f" {unidad}" if unidad else ""
    if r["s"] is None:
        return "Con un solo dato no se puede medir la dispersión: se necesitan al menos 2 mediciones."
    txt = (f"Las mediciones se concentran alrededor de {fmt(r['media'])}{u}. "
           f"La desviación estándar muestral s = {fmt(r['s'])}{u} indica que, en promedio, "
           f"cada dato se aleja unos {fmt(r['s'])}{u} de la media; "
           f"el rango típico es de {fmt(r['media'] - r['s'])} a {fmt(r['media'] + r['s'])}{u}. ")
    if r["cv"] is not None:
        cv = r["cv"]
        nivel = ("muy baja" if cv < 5 else "baja" if cv < 10 else
                 "moderada" if cv < 20 else "alta")
        calidad = ("las mediciones son muy consistentes (buena precisión)." if cv < 10 else
                   "hay variación apreciable entre mediciones." if cv < 20 else
                   "las mediciones son poco consistentes; conviene revisar el procedimiento o repetir.")
        txt += (f"El coeficiente de variación es {fmt(cv, 2)} %, es decir, dispersión {nivel}: {calidad} ")
    txt += "Si los datos son aproximadamente normales, cerca del 68 % cae dentro de x̄ ± s."
    return txt


# ───────────────────────── Datos experimentales y unidades ─────────────────────────

UNIDADES = {
    "Corriente eléctrica": {"A": 1, "mA": 1e-3, "µA": 1e-6},
    "Voltaje": {"V": 1, "mV": 1e-3, "kV": 1e3},
    "Resistencia": {"Ω": 1, "kΩ": 1e3, "mΩ": 1e-3},
    "Longitud": {"m": 1, "cm": 1e-2, "mm": 1e-3, "km": 1e3},
    "Tiempo": {"s": 1, "ms": 1e-3, "min": 60, "h": 3600},
    "Masa": {"kg": 1, "g": 1e-3, "mg": 1e-6},
    "Fuerza": {"N": 1, "mN": 1e-3, "kN": 1e3},
}


def convertir(valor, magnitud, de, a):
    f = UNIDADES[magnitud]
    return valor * f[de] / f[a]


def redondeo_incertidumbre(media, u):
    """Regla usual: incertidumbre con 1 cifra significativa (2 si empieza en 1)."""
    if not u or not math.isfinite(u) or u <= 0:
        return media, u, None
    exp = math.floor(math.log10(u))
    primera = int(u / 10 ** exp)
    dec = -exp + (1 if primera == 1 else 0)
    return round(media, dec), round(u, dec), dec


def medicion(d):
    n = len(d)
    r = descriptiva(d)
    if n < 2:
        return None
    u = r["s"] / math.sqrt(n)
    m_r, u_r, dec = redondeo_incertidumbre(r["media"], u)
    rel = abs(u / r["media"]) * 100 if r["media"] != 0 else None
    return dict(r=r, u=u, media_r=m_r, u_r=u_r, dec=dec, rel=rel)


def fmt_dec(x, dec):
    if dec is None:
        return fmt(x)
    return f"{x:.{max(dec, 0)}f}"


# ───────────────────────── Tablas de frecuencia ─────────────────────────


def sturges(n):
    return max(1, math.ceil(1 + math.log2(n)))


def tabla_frecuencias(d, k=None):
    a = np.array(d, dtype=float)
    n = a.size
    k = int(k) if k else sturges(n)
    k = max(1, k)
    lo, hi = float(a.min()), float(a.max())
    if hi == lo:
        lo, hi, k = lo - 0.5, hi + 0.5, 1
    edges = np.linspace(lo, hi, k + 1)
    f, _ = np.histogram(a, bins=edges)
    marcas = (edges[:-1] + edges[1:]) / 2
    clases = [f"[{fmt(edges[i], 3)} , {fmt(edges[i + 1], 3)}{']' if i == k - 1 else ')'}"
              for i in range(k)]
    fr = f / n
    df = pd.DataFrame({"Clase": clases, "Marca de clase": [fmt(x, 3) for x in marcas],
                       "f": f, "fr": [round(x, 4) for x in fr], "F": np.cumsum(f),
                       "%": [round(x * 100, 2) for x in fr]})
    return df, edges, k, (hi - lo) / k


# ───────────────────────── Probabilidad ─────────────────────────


def norm_cdf(z):
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def norm_pdf(x, mu, sigma):
    return math.exp(-0.5 * ((x - mu) / sigma) ** 2) / (sigma * math.sqrt(2 * math.pi))


def norm_ppf(p):
    """Inversa de Φ por bisección (0<p<1)."""
    lo, hi = -10.0, 10.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if norm_cdf(mid) < p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def binom_pmf(n, p, k):
    return math.comb(n, k) * p ** k * (1 - p) ** (n - k)


# ───────────────────────── Regresión y correlación ─────────────────────────


def regresion(x, y):
    if len(x) != len(y):
        raise ValueError(f"x tiene {len(x)} datos y y tiene {len(y)}: deben tener la misma cantidad.")
    n = len(x)
    if n < 3:
        raise ValueError("Se necesitan al menos 3 pares de datos para una regresión confiable.")
    xa, ya = np.array(x, float), np.array(y, float)
    mx, my = xa.mean(), ya.mean()
    sxx = float(((xa - mx) ** 2).sum())
    syy = float(((ya - my) ** 2).sum())
    sxy = float(((xa - mx) * (ya - my)).sum())
    if sxx == 0:
        raise ValueError("Todos los valores de x son iguales: no se puede ajustar una recta.")
    b = sxy / sxx
    a = my - b * mx
    r = sxy / math.sqrt(sxx * syy) if syy > 0 else None
    return dict(n=n, mx=float(mx), my=float(my), sxx=sxx, syy=syy, sxy=sxy,
                b=b, a=a, r=r, r2=(r ** 2 if r is not None else None))


def tabla_regresion(x, y, rg):
    return pd.DataFrame({"x": x, "y": y, "x − x̄": [v - rg["mx"] for v in x],
                         "y − ȳ": [v - rg["my"] for v in y],
                         "(x−x̄)(y−ȳ)": [(a - rg["mx"]) * (b - rg["my"]) for a, b in zip(x, y)],
                         "(x−x̄)²": [(a - rg["mx"]) ** 2 for a in x]})


def interpretar_r(r):
    if r is None:
        return "Todos los valores de y son iguales, por lo que r no está definido."
    ar = abs(r)
    fuerza = ("muy fuerte" if ar >= 0.9 else "fuerte" if ar >= 0.7 else
              "moderada" if ar >= 0.4 else "débil" if ar >= 0.1 else "prácticamente nula")
    sentido = "positiva (al aumentar x, y tiende a aumentar)" if r > 0 else \
              "negativa (al aumentar x, y tiende a disminuir)"
    if ar < 0.1:
        return f"r = {fmt(r)}: correlación lineal prácticamente nula."
    return (f"r = {fmt(r)}: correlación lineal {fuerza} y {sentido}. "
            f"El modelo lineal explica el {fmt(r * r * 100, 1)} % de la variación de y (r²). "
            "Recuerda: correlación no implica causalidad.")


# ───────────────────────── Ejemplos resueltos (≥ 10) ─────────────────────────

EJEMPLOS = [
    dict(titulo="Ejemplo de prueba del ingeniero: corriente (A)", tipo="exp",
         enunciado="Mediciones de corriente (A): 2.1, 2.3, 2.2, 2.4 y 2.0. Calcula la media, la desviación estándar muestral e interprétala.",
         datos=[2.1, 2.3, 2.2, 2.4, 2.0], magnitud="Corriente eléctrica", unidad="A"),
    dict(titulo="Tiempo de caída de un objeto", tipo="exp",
         enunciado="Cinco cronometrajes de una caída libre (s): 0.52, 0.55, 0.50, 0.53, 0.54. Da el resultado como media ± incertidumbre.",
         datos=[0.52, 0.55, 0.50, 0.53, 0.54], magnitud="Tiempo", unidad="s"),
    dict(titulo="Masas de un lote de piezas", tipo="desc",
         enunciado="Masas (g) de 7 piezas: 12, 15, 15, 18, 20, 15, 22. Halla media, mediana, moda y rango.",
         datos=[12, 15, 15, 18, 20, 15, 22], unidad="g"),
    dict(titulo="Longitud de un resorte con conversión de unidades", tipo="exp",
         enunciado="Longitudes (mm): 152, 150, 151, 153, 149, 151. Calcula la media ± incertidumbre y exprésala en metros.",
         datos=[152, 150, 151, 153, 149, 151], magnitud="Longitud", unidad="mm", destino="m"),
    dict(titulo="Tabla de frecuencias e histograma", tipo="freq",
         enunciado="Temperaturas (°C) de 20 lecturas. Construye la tabla de frecuencias y el histograma.",
         datos=[21, 22, 22, 23, 23, 23, 24, 24, 24, 24, 25, 25, 25, 26, 26, 27, 27, 28, 29, 31], k=5),
    dict(titulo="Probabilidad clásica con un dado", tipo="clasica",
         enunciado="Se lanza un dado justo. ¿Cuál es la probabilidad de obtener un número par?", fav=3, tot=6),
    dict(titulo="Probabilidad de la unión", tipo="union",
         enunciado="Si P(A)=0.40, P(B)=0.50 y P(A∩B)=0.20, calcula P(A∪B) y verifica si A y B son independientes.",
         pa=0.40, pb=0.50, pab=0.20),
    dict(titulo="Distribución binomial", tipo="binom",
         enunciado="Se lanza una moneda justa 5 veces. ¿Cuál es la probabilidad de obtener exactamente 3 caras?", n=5, p=0.5, k=3),
    dict(titulo="Normal: probabilidad acumulada", tipo="normal",
         enunciado="El rendimiento de un motor sigue una normal con μ = 70 y σ = 10. Calcula P(X < 85).",
         mu=70, sigma=10, modo="menor", a=85, b=None),
    dict(titulo="Normal: probabilidad entre dos valores", tipo="normal",
         enunciado="Con μ = 100 y σ = 15, calcula P(85 < X < 115).", mu=100, sigma=15, modo="entre", a=85, b=115),
    dict(titulo="Ley de Hooke: regresión lineal", tipo="reg",
         enunciado="Fuerza (N) contra elongación (m): x = 0.02, 0.04, 0.06, 0.08, 0.10; y = 0.9, 2.1, 2.9, 4.1, 5.0. Halla la recta, r y la constante k del resorte.",
         x=[0.02, 0.04, 0.06, 0.08, 0.10], y=[0.9, 2.1, 2.9, 4.1, 5.0], nx="Elongación x (m)", ny="Fuerza y (N)", x_pred=0.05),
    dict(titulo="Desviación poblacional vs. muestral", tipo="popsam",
         enunciado="Con los datos 4, 8, 6, 5, 7 compara la desviación estándar poblacional (σ) y la muestral (s).",
         datos=[4, 8, 6, 5, 7]),
]

# ───────────────────────── Práctica con retroalimentación ─────────────────────────

TIPOS_PRACTICA = {
    "media": "Media aritmética",
    "mediana": "Mediana",
    "s": "Desviación estándar muestral",
    "normal": "Probabilidad normal P(X < x)",
    "pendiente": "Pendiente de la regresión",
    "correlacion": "Coeficiente de correlación r",
    "clasica": "Probabilidad con dos dados",
}


def generar_ejercicio(tipo, rng):
    if tipo in ("media", "mediana", "s"):
        n = rng.randint(5, 8)
        datos = [round(rng.uniform(2, 30), 1) for _ in range(n)]
        r = descriptiva(datos)
        lista = ", ".join(fmt(x) for x in datos)
        if tipo == "media":
            return dict(tipo=tipo, datos=datos, respuesta=r["media"], tol=0.01,
                        enunciado=f"Calcula la **media** de: {lista}. (2 decimales)", pistas=[])
        if tipo == "mediana":
            return dict(tipo=tipo, datos=datos, respuesta=r["mediana"], tol=0.01,
                        enunciado=f"Calcula la **mediana** de: {lista}. (2 decimales)", pistas=[])
        return dict(tipo=tipo, datos=datos, respuesta=r["s"], tol=0.011,
                    enunciado=f"Calcula la **desviación estándar muestral** s de: {lista}. (2 decimales)",
                    pistas=[(r["sigma"], "Parece que dividiste entre n. Para la desviación muestral se divide entre n − 1."),
                            (r["var_m"], "Ese valor es la varianza s². Falta sacar la raíz cuadrada.")])
    if tipo == "normal":
        mu, sigma = rng.choice([(50, 8), (70, 10), (100, 15), (12, 2), (200, 25)])
        x = mu + rng.choice([-2, -1, -0.5, 0.5, 1, 1.5, 2]) * sigma
        z = (x - mu) / sigma
        p = norm_cdf(z)
        return dict(tipo=tipo, mu=mu, sigma=sigma, x=x, respuesta=p, tol=0.002,
                    enunciado=f"X ~ Normal(μ = {mu}, σ = {sigma}). Calcula **P(X < {fmt(x)})**. (3 decimales)",
                    pistas=[(1 - p, "Calculaste la cola derecha P(X > x). Aquí piden la probabilidad hacia la izquierda."),
                            (z, "Ese valor es z. Falta buscar Φ(z) para obtener la probabilidad.")])
    if tipo in ("pendiente", "correlacion"):
        m_ = rng.choice([0.5, 1.5, 2, 2.5, 3, -1.5, -2])
        x = [1, 2, 3, 4, 5, 6][: rng.randint(5, 6)]
        y = [round(m_ * xi + rng.uniform(-1, 1) + 3, 1) for xi in x]
        rg = regresion(x, y)
        if tipo == "pendiente":
            return dict(tipo=tipo, x=x, y=y, respuesta=rg["b"], tol=0.02,
                        enunciado=f"Con x = {', '.join(map(fmt, x))} y y = {', '.join(map(fmt, y))}, calcula la **pendiente b** de la recta de regresión. (2 decimales)",
                        pistas=[(rg["r"], "Ese valor es r (correlación), no la pendiente b = Sxy / Sxx."),
                                (rg["a"], "Ese valor es el intercepto a. Piden la pendiente b.")])
        return dict(tipo=tipo, x=x, y=y, respuesta=rg["r"], tol=0.011,
                    enunciado=f"Con x = {', '.join(map(fmt, x))} y y = {', '.join(map(fmt, y))}, calcula el **coeficiente de correlación r**. (2 decimales)",
                    pistas=[(rg["r2"], "Ese valor es r². Falta sacar la raíz cuadrada (y conservar el signo de la pendiente)."),
                            (rg["b"], "Ese valor es la pendiente b, no r.")])
    # clasica: dos dados
    suma = rng.randint(3, 11)
    fav = sum(1 for i in range(1, 7) for j in range(1, 7) if i + j == suma)
    return dict(tipo="clasica", suma=suma, fav=fav, tot=36, respuesta=fav / 36, tol=0.006,
                enunciado=f"Se lanzan dos dados justos. ¿Cuál es la probabilidad de que la suma sea **{suma}**? (decimal con 3 decimales o fracción, ej. 1/6)",
                pistas=[(1 / 6, "Recuerda que hay 36 resultados posibles, no 6.")])


def parse_respuesta(txt):
    t = (txt or "").strip().replace(",", ".")
    if not t:
        return None, "Escribe tu respuesta."
    try:
        if "/" in t:
            a, b = t.split("/", 1)
            return float(a) / float(b), None
        return float(t), None
    except (ValueError, ZeroDivisionError):
        return None, "No entendí tu respuesta. Escribe un número (ej. 2.35 o 1/6)."


def evaluar(ej, valor):
    """Devuelve (correcto, mensaje)."""
    if abs(valor - ej["respuesta"]) <= ej["tol"]:
        return True, f"¡Ka-chow! Correcto. El valor es {fmt(ej['respuesta'], 4)}."
    for val, msg in ej.get("pistas", []):
        if val is not None and abs(valor - val) <= ej["tol"] * 1.5:
            return False, msg
    return False, "Todavía no. Revisa la fórmula y la sustitución paso a paso (abre la solución para comparar)."


# ───────────────────────── Interpretación de preguntas libres ─────────────────────────

_NUM = r"(-?\d+(?:\.\d+)?)"


def interpretar_pregunta(texto):
    """Analiza una pregunta escrita en español y decide qué calcular."""
    t = (texto or "").lower().strip()
    if not t:
        return dict(tipo="vacio", mensaje="Escribe una pregunta, por ejemplo: «media y desviación de 2.1, 2.3, 2.2, 2.4, 2.0».")
    # Regresión / correlación: "x: ... y: ..."
    mxy = re.search(r"\bx\s*[:=]\s*([^a-zA-Z]+?)\s*\by\s*[:=]\s*([^a-zA-Z]+)", t)
    if mxy:
        x, ex = parse_numbers(mxy.group(1))
        y, ey = parse_numbers(mxy.group(2))
        if ex or ey:
            return dict(tipo="error", mensaje=ex or ey)
        return dict(tipo="regresion", x=x, y=y)
    # Normal
    if "normal" in t or re.search(r"\bp\s*\(\s*x", t):
        mu = re.search(r"(?:media|μ|mu)\s*(?:=|de|es)?\s*" + _NUM, t)
        sg = re.search(r"(?:desviaci[oó]n(?:\s+est[aá]ndar)?|σ|sigma)\s*(?:=|de|es)?\s*" + _NUM, t)
        entre = re.search(r"entre\s*" + _NUM + r"\s*(?:y|e|-)\s*" + _NUM, t) or \
            re.search(_NUM + r"\s*<\s*x\s*<\s*" + _NUM, t)
        menor = re.search(r"(?:menor(?:\s+que)?|<|x\s*<)\s*" + _NUM, t)
        mayor = re.search(r"(?:mayor(?:\s+que)?|>|x\s*>)\s*" + _NUM, t)
        if mu and sg:
            mu_v, sg_v = float(mu.group(1)), float(sg.group(1))
            if sg_v <= 0:
                return dict(tipo="error", mensaje="La desviación estándar debe ser mayor que 0.")
            if entre:
                a, b = sorted((float(entre.group(1)), float(entre.group(2))))
                return dict(tipo="normal", mu=mu_v, sigma=sg_v, modo="entre", a=a, b=b)
            if menor:
                return dict(tipo="normal", mu=mu_v, sigma=sg_v, modo="menor", a=float(menor.group(1)), b=None)
            if mayor:
                return dict(tipo="normal", mu=mu_v, sigma=sg_v, modo="mayor", a=float(mayor.group(1)), b=None)
        return dict(tipo="error", mensaje="Para la normal necesito μ, σ y la condición. Ej.: «normal con media 70 y desviación 10, P(X<85)». También puedes usar el módulo de Probabilidad.")
    # Estadística descriptiva sobre una lista de números
    nums = re.findall(_NUM, t)
    if not nums:
        return dict(tipo="error", mensaje="No encontré datos numéricos. Ejemplo: «mediana de 4, 8, 6, 5, 7».")
    datos = [float(v) for v in nums]
    foco = None
    for clave, palabras in [("mediana", ["mediana"]), ("moda", ["moda"]), ("rango", ["rango"]),
                            ("varianza", ["varianza"]), ("desviacion", ["desviaci", "desv"]),
                            ("media", ["media", "promedio"]),
                            ("frecuencias", ["frecuencia", "histograma"])]:
        if any(p in t for p in palabras):
            foco = clave
            break
    return dict(tipo="descriptiva", datos=datos, foco=foco)
