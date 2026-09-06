
# Aplicación web – Círculo de Mohr

Aplicación didáctica interactiva desarrollada para:

**Material didáctico Estabilidad 2 – F.I. – UNNE**  
**Ing. Ricardo Barrios D’Ambra**

## Ejecutar localmente

1. Instalar Python 3.
2. Abrir una terminal en esta carpeta.
3. Instalar dependencias:

```bash
pip install -r requirements.txt
```

4. Ejecutar:

```bash
streamlit run app.py
```

Se abrirá automáticamente en el navegador.

## Publicarla en Internet con Streamlit Community Cloud

1. Crear una cuenta en GitHub si todavía no tiene.
2. Crear un repositorio nuevo.
3. Subir a ese repositorio:
   - `app.py`
   - `requirements.txt`
4. Ingresar a Streamlit Community Cloud.
5. Elegir **Create app** / **New app**.
6. Seleccionar el repositorio.
7. Como archivo principal elegir `app.py`.
8. Publicar.

Streamlit generará una dirección web que podrá compartirse en:
- Moodle
- Instagram
- LinkedIn
- WhatsApp
- correo electrónico

Los alumnos solamente necesitarán abrir el enlace desde un navegador.

## Convenciones utilizadas

- σ positiva: tracción.
- τxy positiva: tendencia a hacer girar el elemento diferencial en sentido horario.
- τyx = −τxy.
- α positivo: medido desde la vertical en sentido antihorario.
- Punto principal P obtenido por la intersección de:
  - la traza vertical que pasa por (σx, τxy)
  - la traza horizontal que pasa por (σy, τyx)
