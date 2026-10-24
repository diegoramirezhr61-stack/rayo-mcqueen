# ⚡ Rayo McQueen — Guía rápida (Windows + Visual Studio Code)

## 0. Antes de empezar (una sola vez)
1. Instala **Python 3.10 o superior** desde python.org (marca ✅ *Add python.exe to PATH*).
2. Instala **Visual Studio Code** y, dentro, la extensión **Python** (Microsoft).
3. Descomprime la carpeta `rayo_mcqueen` y ábrela: **File ▸ Open Folder…**
4. Abre la terminal de VS Code: **Terminal ▸ New Terminal** (atajo `Ctrl + ñ` o `Ctrl + \``).

## 1. Poner a correr el programa (terminal de VS Code)
```
python --version
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```
Se abre solo el navegador en `http://localhost:8501`. Para detenerlo: `Ctrl + C` en la terminal.

**Si `activate` da error de permisos (PowerShell)**, ejecuta una vez:
```
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```
y repite `.venv\Scripts\activate`. (O cambia la terminal a *Command Prompt* con la flecha ▾ junto al “+”.)

**Si `python` no se reconoce**, prueba `py -m venv .venv` y luego `py -m pip install -r requirements.txt`.

**Mac / Linux:** `python3 -m venv .venv` · `source .venv/bin/activate` · `pip install -r requirements.txt` · `streamlit run app.py`

## 2. Antes de publicar: pon sus datos
Abre `app.py` y edita estas líneas (arriba del archivo):
```python
INTEGRANTES = ["Marck [APELLIDOS]", "[NOMBRE DEL COMPAÑERO/A]"]
SECCION = "A"
```
Guarda (`Ctrl + S`) y recarga el navegador.

## 3. Publicar el enlace (requisito de Canvas)
1. Crea una cuenta en **github.com** y un repositorio **público** nuevo (ej. `rayo-mcqueen`), sin README.
2. Instala **Git** (git-scm.com). En la terminal de VS Code:
```
git init
git add .
git commit -m "Rayo McQueen - Asistente de Estadistica"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/rayo-mcqueen.git
git push -u origin main
```
3. Entra a **share.streamlit.io**, inicia sesión con GitHub ▸ **Create app** ▸ elige tu repositorio, rama `main`, archivo `app.py` ▸ **Deploy**.
4. Cuando termine, copia el enlace `https://….streamlit.app`, ábrelo en una ventana de incógnito (debe abrir **sin pedir inicio de sesión**) y pégalo en Canvas y en el informe.

⚠️ Streamlit Community Cloud “duerme” las apps tras ~12 horas sin visitas: **ábrelo justo antes de la revisión** para que esté despierto (si aparece la pantalla de “wake up”, pulsa el botón y espera unos segundos).

## 4. Mapa del proyecto (para explicarlo al ingeniero)
| Archivo | Qué hace |
|---|---|
| `motor.py` | Todos los **cálculos** (media, s, normal, regresión, unidades, ejercicios, intérprete de preguntas). Sin interfaz. |
| `app.py` | La **interfaz** Streamlit con el tema de Cars: menú, formularios, gráficas, fórmulas paso a paso. |
| `requirements.txt` | Librerías que necesita (Streamlit, NumPy, Pandas, Matplotlib). |
| `.streamlit/config.toml` | Colores del tema (rojo Rayo, crema, amarillo). |

Ideas clave que deben saber explicar: media y desviación estándar muestral (`÷ n−1`) vs poblacional (`÷ n`), incertidumbre `u = s/√n`, el valor `z` y la tabla normal Φ(z), y qué significan `r` y la pendiente `b` en la regresión.

## 5. Render (publicar) — configuración
- **Build Command:** `pip install -r requirements.txt`
- **Start Command (usa ESTE, fuerza el tema claro aunque falte .streamlit):**
```
streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true --theme.base light --theme.backgroundColor "#FFF8E7" --theme.secondaryBackgroundColor "#FFE9A8" --theme.textColor "#14181F" --theme.primaryColor "#C8102E"
```
- Si Chrome ofrece traducir la página, elige *Nunca traducir español*; la app ya lo desactiva sola.
