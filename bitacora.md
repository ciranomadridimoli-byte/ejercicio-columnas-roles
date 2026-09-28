# Bitácora

## ¿Qué ventajas tienen las estructuras elegidas respecto de otras vistas en la teoría?

Para COLUMNAS usé un diccionario donde la clave es el nombre de la columna y el valor es otro diccionario con "tipo" y "completitud". Lo elegí por tres cosas. Primero, puedo ir directo a una columna por su nombre, por ejemplo columnas["ITF"]["completitud"], sin recorrer nada, y como el filtro y el map() del informe hacen eso todo el tiempo, se nota. Con una lista de tuplas o de diccionarios tendría que buscar la columna recorriendo la lista cada vez. Segundo, las claves no se pueden repetir, así que no hay dos columnas con el mismo nombre. Y tercero, ["completitud"] se entiende solo, en cambio con una tupla tendría que acordarme qué dato era el [2]. Un conjunto no me servía porque no guarda datos asociados ni orden.

ROLES es un diccionario de diccionarios. Lo bueno del diccionario interno es que puede tener campos opcionales: "minimo" solo está en los roles que lo usan y lo leo con .get(), que devuelve None si no existe. Con una tupla tendría que dejar una posición reservada aunque no haya dato. Las columnas de cada rol van en una lista porque es algo que se recorre. CRITERIOS_VALIDOS y ORDENES_VALIDOS son tuplas porque son valores fijos que no quiero que se modifiquen. Y FUNCIONES_DE_ORDEN es un diccionario que relaciona cada criterio con su función de orden.

## ¿Qué valores elegí para los roles y los porcentajes de completitud, y cómo garantizo que se pueda validar con distintos roles, criterios y umbrales?

Puse completitudes entre 55 y 100, con decimales, para que los umbrales se noten de verdad. Los tres roles los armé para cubrir todas las variantes que pide el enunciado:

- docente: ordena por nombre, ascendente (A) y no tiene mínimo.
- investigador: ordena por completitud, descendente (B) y tiene mínimo 60.
- analista: ordena por completitud, ascendente (A) y tiene mínimo 50.

Así pruebo los dos criterios, los dos sentidos y roles con y sin umbral. Con el mínimo de 60, GDECCFR (55.0) queda afuera del informe del investigador. Con los datos que tengo, el mínimo de 50 del analista no saca ninguna columna, pero para verlo en acción alcanza con subirlo en ROLES (con 70, por ejemplo, se va CAT_OCUP, que tiene 61.2).

Para probar otros casos no hace falta tocar las funciones: generar_informe recibe rol, columnas y roles por parámetro, entonces solo cambio los datos. También se puede probar sin rol, con un rol que no existe y con un criterio u orden inválido, y en ningún caso se rompe el programa.

## ¿Por qué conviene separar la configuración de los roles (ROLES) de la lógica que genera el informe?

Porque así tengo que tocar menos código. Agregar un rol, cambiarle el orden o modificar un umbral es editar datos en ROLES y listo, las funciones quedan como están. También hay menos riesgo de romper algo, porque la lógica que ya anda no se toca cada vez que cambia una regla. Además toda la configuración queda en un solo lugar, y las mismas funciones sirven para cualquier configuración porque roles y columnas llegan por parámetro, lo que también ayuda a probarlas.

## ¿Qué parámetros se pueden definir con valores por defecto?

- rol=None en generar_informe e imprimir_informe: si no se pasa rol, se muestran todas las columnas.
- columnas=COLUMNAS y roles=ROLES en las funciones que los usan.
- criterio y orden cuando el rol no los define, con config.get("criterio", CRITERIO_DEFAULT) y config.get("orden", ORDEN_DEFAULT).
- minimo y maximo: si no están, .get() devuelve None y no se filtra nada.

CRITERIO_DEFAULT ("completitud") y ORDEN_DEFAULT ("B") están definidos una sola vez, arriba de todo.

## Si agrego una nueva columna al dataset, ¿en qué partes del código impacta? ¿Y si solo quiero que un rol existente la incluya?

Solo la agrego a COLUMNAS con su tipo y su completitud. El informe sin rol ya la incluye solo, porque arma la lista de nombres con list(COLUMNAS.keys()). En los roles no aparece hasta que la sume a su lista "columnas". Si quiero que solo un rol existente la tenga, agrego el nombre en la lista de ese rol en ROLES. En ninguno de los dos casos hay que cambiar una función.

## ¿Qué pasaría si un rol tuviera un criterio de orden distinto de "nombre" o "completitud" (por ejemplo, "promedio")?

Lo detecta generar_informe, que se fija si el criterio está en CRITERIOS_VALIDOS. Si no está, avisa por pantalla y usa CRITERIO_DEFAULT. Además, clave_de_orden tiene otra protección: usa FUNCIONES_DE_ORDEN.get(criterio, ...) con la función por defecto de respaldo. O sea que el programa no falla, solo avisa. Si quisiera que "promedio" fuera un criterio válido, tendría que agregar su función a FUNCIONES_DE_ORDEN y su nombre a CRITERIOS_VALIDOS.

## ¿Qué cambiaría si por defecto el informe debiera salir según uno de los roles?

Definiría una constante ROL_DEFAULT = "docente" (o el rol que pidan). En obtener_config_rol, cuando rol es None, devolvería roles[ROL_DEFAULT] en vez de armar el diccionario con todas las columnas. CRITERIO_DEFAULT y ORDEN_DEFAULT seguirían sirviendo de respaldo si un rol no define esos campos. El resto del programa queda igual.

## Errores encontrados y cómo los resolví

Me costó muchísimo entender la indentación. Venía de otros lenguajes donde indentar mal no cambia el funcionamiento del programa, y en Python sí.

Con el filtro de completitud, lo generalicé con construir_filtro_completitud, que soporta "minimo", "maximo" o los dos según lo que diga el rol. Así se adapta mejor a los cambios.

Con los criterios de orden, al principio usaba if/else y cada criterio nuevo me obligaba a editar la función. Lo cambié por el diccionario FUNCIONES_DE_ORDEN.

Con la entrada del usuario, si escribía un espacio de más el rol quedaba como "inexistente". Lo arreglé con .strip() en main().

## Modificaciones pedidas en la corrección

### Rol analista sin PONDERA ni ANO4

Fui a ROLES, busqué "analista" y edité su lista "columnas". Antes era ["ESTADO", "CAT_OCUP", "ITF", "MAS_500", "ANO4", "TRIMESTRE"]. Ahí vi que PONDERA no estaba en esa lista, o sea que el rol ya la excluía, y lo único que tuve que sacar fue "ANO4". Ahora queda ["ESTADO", "CAT_OCUP", "ITF", "MAS_500", "TRIMESTRE"]. No toqué ninguna función, porque el rol es solo un dato y el informe lee la lista como esté. Al correr el programa con el rol analista salen cinco columnas, sin ANO4 ni PONDERA, y siguen ordenadas por completitud de menor a mayor.

### Tipo de MAS_500 de str a bool

Cambié "str" por "bool" en la entrada de MAS_500 dentro de COLUMNAS y nada más. En el resto del código casi no hay impacto, porque el tipo no lo uso para decidir nada: solo se lee en imprimir_informe para mostrarlo en la columna Tipo. Como "bool" tiene cuatro letras y esa columna tiene ancho 6, la tabla sigue alineada igual. El filtro de completitud, el orden por nombre o por completitud y las validaciones de rol, criterio y orden no miran el tipo, así que siguen funcionando igual.

Lo que sí cambia es el significado del dato. Antes MAS_500 era un texto con "N" o "S" y ahora sería un verdadero o falso (por ejemplo, True para los aglomerados de 500.000 habitantes o más). Igual, en el programa "tipo" es solo una descripción escrita y no hay datos reales cargados, así que no hay ninguna conversión ni chequeo para actualizar. Si algún día se agregara un criterio para ordenar por tipo, ahí sí cambiaría el resultado, porque "bool" va antes que "int" en orden alfabético y antes "str" iba después.

### Uso de filter() y map()

Usé las dos. filter() está en filtrar_por_completitud, para quedarme con las columnas que cumplen el mínimo o el máximo, y map() está en imprimir_informe, para armar la línea de texto de cada columna.

Con un for tendría que crear una lista vacía, recorrer los nombres, preguntar con un if y agregar con append. Con filter() eso queda en una sola línea y se lee qué quiero (quedarme con los que cumplen) sin seguir el paso a paso. Además, la condición queda separada en la función cumple, que se arma según el rol, y por eso pasar de mínimo a máximo no me obliga a tocar el filter. Con map() pasa algo parecido: aplico la misma transformación a cada nombre sin variables auxiliares.

Otra cosa que tuve en cuenta es que filter() y map() no devuelven listas sino iteradores, por eso los envuelvo en list(). En imprimir_informe hace falta, porque después pregunto if not filas y un iterador siempre da verdadero aunque no tenga elementos, entonces el mensaje de que ninguna columna cumple los criterios nunca aparecería. Igual no son siempre la mejor opción: si la condición fuera larga o tuviera varios pasos, un for se entendería mejor.

### Pruebas

Las pruebas las hice en un jupyter notebook, corriendo los dos códigos (el original y el modificado). Llamando a las funciones de impresión me di cuenta de que las modificaciones andaban y de que la función quedó eficiente pensando en cambios futuros. Podría haberlo resuelto de forma más sencilla sin usar tantos métodos, pero quería asegurarme de que el código se adapte rápido a lo que me pidieran.

## Aclaración

La consigna pedía solo un porcentaje mínimo de completitud, y eso es justo lo que hace mi función: si un rol tiene la clave "minimo", se muestran las columnas con completitud mayor o igual a ese valor, y si el rol no la tiene, no se filtra nada, que es el caso opcional que describe el enunciado. Igual, en lugar de escribir la comparación >= directo en el código, armé la función construir_filtro_completitud, que lee de la configuración del rol tanto "minimo" como "maximo" y devuelve una función que decide si una columna cumple. Lo hice pensando en las modificaciones que me podían pedir en la corrección. Si en vez de un mínimo piden un máximo, o los dos a la vez, alcanza con cambiar o agregar la clave en ROLES y no hay que tocar ninguna función. Si hubiera dejado el >= escrito a mano, cada cambio de ese tipo me habría obligado a reescribir el filtro y a volver a probar todo. De esta forma la regla queda como un dato de configuración y la lógica de filtrado queda estable.