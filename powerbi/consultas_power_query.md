# Consultas de Power Query y medidas del dashboard

El dashboard (`dashboard/dashboard-cultivos-clima.pbix`) carga los cuatro CSV de esta carpeta (`powerbi/`), que genera el notebook `05-sql_consultas.ipynb` a partir de las vistas de la base SQL. Son un corte histórico que no cambia, así que no hay conexión a la base.

## Cómo reconectar el dashboard

Cada consulta tiene **una sola ruta**, en la primera línea del paso `Origen`. Si clona el repositorio en otra carpeta, hay que cambiarla en las cuatro consultas: *Transformar datos*, seleccionar la consulta, *Editor avanzado*, editar la ruta, *Listo* y *Cerrar y aplicar*.

Ruta usada en este documento: `E:\PROYECTOS PYTHON\clima-rendimiento-cultivos-argentina\powerbi\`

## 1. `01-clima_rendimiento` (vista `v_clima_rendimiento`, 47.358 filas)

```
let
    Origen = Csv.Document(File.Contents("E:\PROYECTOS PYTHON\clima-rendimiento-cultivos-argentina\powerbi\v_clima_rendimiento.csv"), [Delimiter=",", Columns=10, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Encabezados promovidos" = Table.PromoteHeaders(Origen, [PromoteAllScalars=true]),
    #"Tipo cambiado con configuración regional" = Table.TransformColumnTypes(#"Encabezados promovidos", {{"TMAX", type number}, {"TMIN", type number}, {"TMEDIA", type number}, {"HELIOF", type number}, {"PRE_EST", type number}, {"PRECIP", type number}}, "en-US"),
    #"Tipo cambiado" = Table.TransformColumnTypes(#"Tipo cambiado con configuración regional", {{"anio", Int64.Type}, {"rendimiento_kgxha", Int64.Type}})
in
    #"Tipo cambiado"
```

## 2. `02-rendimiento_nacional_cultivo_anio` (vista `v_rendimiento_nacional_cultivo_anio`)

```
let
    Origen = Csv.Document(File.Contents("E:\PROYECTOS PYTHON\clima-rendimiento-cultivos-argentina\powerbi\v_rendimiento_nacional_cultivo_anio.csv"), [Delimiter=",", Columns=5, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Encabezados promovidos" = Table.PromoteHeaders(Origen, [PromoteAllScalars=true]),
    #"Tipo cambiado" = Table.TransformColumnTypes(#"Encabezados promovidos", {{"anio", Int64.Type}}),
    #"Tipo cambiado con configuración regional" = Table.TransformColumnTypes(#"Tipo cambiado", {{"produccion_total_tm", type number}, {"superficie_cosechada_total_ha", type number}, {"rendimiento_ponderado_kgxha", type number}}, "en-US")
in
    #"Tipo cambiado con configuración regional"
```

## 3. `03-rendimiento_provincia_cultivo` (vista `v_rendimiento_provincia_cultivo`)

```
let
    Origen = Csv.Document(File.Contents("E:\PROYECTOS PYTHON\clima-rendimiento-cultivos-argentina\powerbi\v_rendimiento_provincia_cultivo.csv"), [Delimiter=",", Columns=5, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Encabezados promovidos" = Table.PromoteHeaders(Origen, [PromoteAllScalars=true]),
    #"Tipo cambiado con configuración regional" = Table.TransformColumnTypes(#"Encabezados promovidos", {{"produccion_total_tm", type number}, {"superficie_cosechada_total_ha", type number}, {"rendimiento_ponderado_kgxha", type number}}, "en-US")
in
    #"Tipo cambiado con configuración regional"
```

## 4. `04-rendimiento_provincia_cultivo_reciente` (vista `v_rendimiento_provincia_cultivo_reciente`, desde 2010)

```
let
    Origen = Csv.Document(File.Contents("E:\PROYECTOS PYTHON\clima-rendimiento-cultivos-argentina\powerbi\v_rendimiento_provincia_cultivo_reciente.csv"), [Delimiter=",", Columns=5, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Encabezados promovidos" = Table.PromoteHeaders(Origen, [PromoteAllScalars=true]),
    #"Tipo cambiado con configuración regional" = Table.TransformColumnTypes(#"Encabezados promovidos", {{"produccion_total_tm", type number}, {"superficie_cosechada_total_ha", type number}, {"rendimiento_ponderado_kgxha", type number}}, "en-US")
in
    #"Tipo cambiado con configuración regional"
```

## 5. Tablas de dimensión (se construyen desde las consultas 2 y 3, sin ruta)

`Dim_Cultivo`:

```
let
    Origen = #"02-rendimiento_nacional_cultivo_anio",
    #"Otras columnas quitadas" = Table.SelectColumns(Origen, {"cultivo"}),
    #"Duplicados quitados" = Table.Distinct(#"Otras columnas quitadas"),
    #"Filas ordenadas" = Table.Sort(#"Duplicados quitados", {{"cultivo", Order.Ascending}})
in
    #"Filas ordenadas"
```

`Dim_Provincia`:

```
let
    Origen = #"03-rendimiento_provincia_cultivo",
    #"Otras columnas quitadas" = Table.SelectColumns(Origen, {"provincia"}),
    #"Duplicados quitados" = Table.Distinct(#"Otras columnas quitadas"),
    #"Filas ordenadas" = Table.Sort(#"Duplicados quitados", {{"provincia", Order.Ascending}})
in
    #"Filas ordenadas"
```

## 6. Medidas DAX (tabla `02-rendimiento_nacional_cultivo_anio`)

```
Rendimiento Ponderado Promedio =
AVERAGE('02-rendimiento_nacional_cultivo_anio'[rendimiento_ponderado_kgxha])
```

El último año con los 8 cultivos presentes (2024). Avena, centeno y trigo llegan a 2025 y los demás a 2024, y comparar un año con 3 cultivos contra uno con 8 daría una variación falsa.

```
Ultimo Anio Disponible =
VAR TotalCultivos =
    CALCULATE(DISTINCTCOUNT('02-rendimiento_nacional_cultivo_anio'[cultivo]), ALL('02-rendimiento_nacional_cultivo_anio'))
RETURN
MAXX(
    FILTER(
        ALL('02-rendimiento_nacional_cultivo_anio'[anio]),
        CALCULATE(DISTINCTCOUNT('02-rendimiento_nacional_cultivo_anio'[cultivo])) = TotalCultivos
    ),
    '02-rendimiento_nacional_cultivo_anio'[anio]
)
```

```
Rendimiento Promedio Ultimo Anio =
VAR AnioObjetivo = [Ultimo Anio Disponible]
RETURN
CALCULATE(
    [Rendimiento Ponderado Promedio],
    FILTER(ALL('02-rendimiento_nacional_cultivo_anio'[anio]), '02-rendimiento_nacional_cultivo_anio'[anio] = AnioObjetivo)
)
```

```
Rendimiento Promedio Anio Anterior =
VAR AnioObjetivo = [Ultimo Anio Disponible] - 1
RETURN
CALCULATE(
    [Rendimiento Ponderado Promedio],
    FILTER(ALL('02-rendimiento_nacional_cultivo_anio'[anio]), '02-rendimiento_nacional_cultivo_anio'[anio] = AnioObjetivo)
)
```

```
Variación Interanual % =
DIVIDE(
    [Rendimiento Promedio Ultimo Anio] - [Rendimiento Promedio Anio Anterior],
    [Rendimiento Promedio Anio Anterior]
)
```

El cultivo de mayor rendimiento se calcula sobre 2010 en adelante: con toda la serie, el sorgo (desde 1969) parece superar al maíz (desde 1923) por la distinta extensión de las series.

```
Cultivo Mayor Rendimiento Reciente =
VAR T =
    ADDCOLUMNS(
        VALUES('02-rendimiento_nacional_cultivo_anio'[cultivo]),
        "RendProm", CALCULATE([Rendimiento Ponderado Promedio], '02-rendimiento_nacional_cultivo_anio'[anio] >= 2010)
    )
VAR Top = TOPN(1, T, [RendProm], DESC)
RETURN
MAXX(Top, '02-rendimiento_nacional_cultivo_anio'[cultivo])
```

Medidas de la página "Clima y rendimiento" (tabla `01-clima_rendimiento`), todas promedios:

```
Rendimiento Promedio Departamento = AVERAGE('01-clima_rendimiento'[rendimiento_kgxha])
Precipitacion Anual Promedio = AVERAGE('01-clima_rendimiento'[PRECIP])
Temperatura Maxima Promedio = AVERAGE('01-clima_rendimiento'[TMAX])
```

Valores esperados: 2.941,71 kg/ha, 962,92 mm y 24,07 °C.
