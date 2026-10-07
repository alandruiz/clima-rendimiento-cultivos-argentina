# Datos meteorológicos del SMN

Los dos archivos de registros diarios pesan en conjunto unos 94 MB y las tablas que se generan a partir de ellos superan los 100 MB, por eso **no se versionan** en Git (ver `.gitignore`). Para ejecutar los notebooks `02` y `03` hay que descargar los registros y guardarlos en esta carpeta (`data/raw/`) con estos nombres:

| Archivo | Contenido |
|---|---|
| `datos_meteorologicos_1991_2020.xlsx` | Registros diarios 1991–2020 |
| `datos_meteorologicos_desde_2021.lst` | Registros diarios desde 2021 (texto separado por tabulaciones) |
| `estaciones_meteorologicas_2021-2026.xlsx` | Estaciones con su provincia (sí se versiona, pesa 14 KB) |

**Fuente:** Servicio Meteorológico Nacional, [Descarga de datos](https://www.smn.gob.ar/descarga-de-datos). Los diccionarios de variables están en `references/`.

**Archivos que se regeneran al ejecutar los notebooks y no se versionan:**
`data/interim/clima_consolidado.csv` (notebook 02) y `data/processed/clima_procesado.csv` (notebook 02).

**Qué se puede ejecutar sin descargar nada:** los notebooks `01` (cultivos), `04` (exploración) y `05` (SQL) usan solo archivos que sí están en el repositorio.
