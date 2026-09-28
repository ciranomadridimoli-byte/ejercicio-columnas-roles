1. ¿Qué ventajas tienen las estructuras elegidas respecto de otras vistas en la teoría?

COLUMNAS es un diccionario cuya clave es el nombre de la columna y cuyo valor es otro diccionario con "tipo" y "completitud". Esto me da tres ventajas:

Acceso directo por nombre. Escribo columnas["ITF"]["completitud"] sin recorrer nada, y el filtro y el map() del informe lo hacen constantemente. Con una lista de tuplas o de diccionarios tendría que buscar la columna recorriendo la lista cada vez.
Sin nombres repetidos. Las claves son únicas.
Campos con nombre. ["completitud"] se entiende mejor que una posición como [2] en una tupla, donde habría que recordar qué dato es cada uno.

Un conjunto no servía porque no guarda datos asociados ni orden.

ROLES es un diccionario de diccionarios. El diccionario interno permite campos opcionales: "minimo" existe solo en los roles que lo usan y se lee con .get(), que devuelve None si falta. Con una tupla habría que reservar una posición fija incluso para un dato ausente. Las columnas de interés de cada rol van en una lista porque es una secuencia que se recorre. CRITERIOS_VALIDOS y ORDENES_VALIDOS son tuplas porque son valores fijos que no deben modificarse. FUNCIONES_DE_ORDEN es un diccionario que asocia cada criterio con su función de orden.

2. ¿Qué valores elegí para los roles y los porcentajes de completitud, y cómo garantizo que se pueda validar con distintos roles, criterios y umbrales?

Puse completitudes entre 55 y 100, con decimales, para que los rangos tengan efecto real. Los tres roles combinan las variantes que pide el enunciado:

Rol	- Criterio - Orden - Mínimo
docente	- nombre - A (ascendente) - no tiene
investigador - completitud - B (descendente) - 60
analista - completitud	- A (ascendente) - 50

Así se prueban ambos criterios, ambos sentidos y roles con y sin umbral. Con el mínimo de 60, GDECCFR (55.0) queda fuera del informe del investigador. Con los datos actuales, el mínimo de 50 del analista no descarta ninguna columna, pero para verlo filtrar basta subirlo en ROLES (con 70, por ejemplo, se va CAT_OCUP, que tiene 61.2).

Para validar con otros casos no hace falta modificar funciones: generar_informe recibe rol, columnas y roles como parámetros, así que alcanza con cambiar los datos. También se prueban el caso sin rol, un rol inexistente y un criterio u orden inválido, y ninguno rompe el programa.

3. ¿Por qué conviene separar la configuración de los roles (ROLES) de la lógica que genera el informe?

Menos código para cambiar. Agregar un rol, cambiar su orden o modificar un umbral es editar datos en ROLES, sin tocar ninguna función.
Menos riesgo de errores. La lógica ya probada no se modifica cada vez que cambia una regla.
Un solo lugar para consultar. Toda la configuración está concentrada.
Reutilización y pruebas. Las mismas funciones sirven para cualquier configuración porque roles y columnas llegan por parámetro.

4. ¿Qué parámetros se pueden definir con valores por defecto?

rol=None en generar_informe e imprimir_informe: sin rol se informan todas las columnas.
columnas=COLUMNAS y roles=ROLES en las funciones que los usan.
criterio y orden cuando un rol no los define, mediante config.get("criterio", CRITERIO_DEFAULT) y config.get("orden", ORDEN_DEFAULT).
minimo y maximo: si no están, .get() devuelve None y no se aplica restricción.

CRITERIO_DEFAULT ("completitud") y ORDEN_DEFAULT ("B") concentran esos valores en un solo lugar.

5. Si agrego una nueva columna al dataset, ¿en qué partes del código impacta? ¿Y si solo quiero que un rol existente la incluya?

Solo hay que agregarla a COLUMNAS con su tipo y su completitud. El informe sin rol la incluye automáticamente, porque arma la lista de nombres con list(COLUMNAS.keys()). Los roles no la muestran hasta que la agregue a su lista "columnas". Si solo un rol existente debe incluirla, agrego su nombre a la lista de ese rol en ROLES. En ninguno de los dos casos cambia una sola función.

6. ¿Qué pasaría si un rol tuviera un criterio de orden distinto de "nombre" o "completitud" (por ejemplo, "promedio")?

Lo detecto en generar_informe, que compara el criterio contra CRITERIOS_VALIDOS. Si no está, muestra un mensaje por pantalla y usa CRITERIO_DEFAULT. Además, clave_de_orden tiene una segunda protección: usa FUNCIONES_DE_ORDEN.get(criterio, ...) con la función por defecto como respaldo. El programa no falla y avisa del problema. Para que "promedio" fuera un criterio válido, agregaría su función a FUNCIONES_DE_ORDEN y su nombre a CRITERIOS_VALIDOS.

7. ¿Qué cambiaría si por defecto el informe debiera salir según uno de los roles?

Definiría una constante ROL_DEFAULT = "docente" (o el rol que se pida). En obtener_config_rol, cuando rol is None, devolvería roles[ROL_DEFAULT] en lugar de armar el diccionario con todas las columnas. CRITERIO_DEFAULT y ORDEN_DEFAULT seguirían usándose como respaldo cuando un rol no defina esos campos. El resto del programa no cambia.

Errores encontrados y cómo los resolví?

Me costó muchisimo entender la identacion, ya que estaba acostumbrado a otros lenguajes que si identabas mal no interferia en el funcionamiento del programa. 
Lo generalicé con construir_filtro_completitud, que soporta "minimo", "maximo" o ambos según lo que declare el rol, haciendolo mas flexible a cambios.
Criterios de orden con if/else. Cada criterio nuevo obligaba a editar la función. Lo reemplacé por el diccionario FUNCIONES_DE_ORDEN.
Entrada del usuario. Un espacio de más al escribir el rol lo hacía "inexistente". Lo resolví con .strip() en main().

Modificaciones pedidas en la corrección

Rol analista sin PONDERA ni ANO4

Fui a ROLES, busqué "analista" y edité su lista "columnas". Antes era ["ESTADO", "CAT_OCUP", "ITF", "MAS_500", "ANO4", "TRIMESTRE"]. Ahí vi que PONDERA no estaba en esa lista, o sea que el rol ya la excluía, y lo único que tuve que sacar fue "ANO4". Ahora queda ["ESTADO", "CAT_OCUP", "ITF", "MAS_500", "TRIMESTRE"]. No toqué ninguna función, porque el rol es solo un dato y el informe lee la lista como esté. Al correr el programa con el rol analista salen cinco columnas, sin ANO4 ni PONDERA, y siguen ordenadas por completitud de menor a mayor.

Tipo de MAS_500 de str a bool

Cambié "str" por "bool" en la entrada de MAS_500 dentro de COLUMNAS y nada más. En el resto del código casi no hay impacto, porque el tipo no lo uso para decidir nada. Solo se lee en imprimir_informe para mostrarlo en la columna Tipo. Como "bool" tiene cuatro letras y esa columna tiene ancho 6, la tabla sigue alineada igual. El filtro de completitud, el orden por nombre o por completitud y las validaciones de rol, criterio y orden no miran el tipo, así que siguen funcionando igual.

Lo que sí cambia es el significado del dato. Antes MAS_500 era un texto con "N" o "S" y ahora sería un verdadero o falso (por ejemplo, True para los aglomerados de 500.000 habitantes o más). Igual, en el programa "tipo" es solo una descripción escrita y no hay datos reales cargados, así que no hay ninguna conversión ni chequeo para actualizar. Si algún día se agregara un criterio para ordenar por tipo, ahí sí cambiaría el resultado, porque "bool" va antes que "int" en orden alfabético y antes "str" iba después.

Uso de filter() y map()

Usé las dos. filter() está en filtrar_por_completitud, para quedarme con las columnas que cumplen el mínimo o el máximo, y map() está en imprimir_informe, para armar la línea de texto de cada columna.

Con un for habría que crear una lista vacía, recorrer los nombres, preguntar con un if y agregar con append. Con filter() eso queda en una sola línea y se lee qué quiero (quedarme con los que cumplen) sin tener que seguir el paso a paso. Además la condición queda separada en la función cumple, que se arma según el rol, y por eso cambiar de mínimo a máximo no obliga a tocar el filter. Con map() pasa algo parecido: aplico la misma transformación a cada nombre sin variables auxiliares.

Otra cosa que tuve en cuenta es que filter() y map() no devuelven listas sino iteradores, y por eso los envuelvo en list(). En imprimir_informe es necesario, porque después pregunto if not filas y un iterador siempre da verdadero aunque no tenga elementos, entonces el mensaje de que ninguna columna cumple los criterios nunca aparecería. No son la mejor opción siempre: si la condición fuera larga o tuviera varios pasos, un for se entendería mejor.

Las pruebas que realice fueron en el archivo jupyter notebook, y corriendo ambos codigos (original y modificacado). Con la llamada de las funciones de impresion, me di cuenta que funcionaban las modificaciones, y que la funcion quedó eficiente pensando en las futuras modificaciones. Podria haberlo resuelto de forma mas sencilla sin usar tantos metodos, pero queria asegurar que el codigo se adapte rapido a la actividad.

ACLARACION !!!

La consigna pedía solo un porcentaje mínimo de completitud, y eso es justo lo que hace mi función: si un rol tiene la clave "minimo", se muestran las columnas con completitud mayor o igual a ese valor, y si el rol no la tiene, no se filtra nada, que es el caso opcional que describe el enunciado. Igual, en lugar de escribir la comparación >= directamente en el código, armé la función construir_filtro_completitud, que lee de la configuración del rol tanto "minimo" como "maximo" y devuelve una función que decide si una columna cumple. Lo hice pensando en las modificaciones que podían pedirme en la corrección. Si en vez de un mínimo piden un máximo, o los dos a la vez, alcanza con cambiar o agregar la clave en ROLES y no hay que tocar ninguna función. Si hubiera dejado el >= escrito, cada cambio de ese tipo me habría obligado a reescribir el filtro y a volver a probar todo. De esta forma la regla queda como un dato de configuración y la lógica de filtrado queda estable.