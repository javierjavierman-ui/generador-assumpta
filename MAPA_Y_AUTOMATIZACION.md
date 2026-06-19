# Assumpta: mapa de secciones y automatizacion

## 1. Secciones identificadas en el folleto

PDF analizado: `1233-Assumpta-07-06-2026.pdf`.

El folleto es un triptico A4 apaisado de 2 paginas, con 6 paneles.

### Pagina 1

1. **Portada Assumpta**
   - Nombre: ASSUMPTA.
   - Numero: 1233.
   - Fecha: 7 de junio de 2026.
   - Parroquia: Asuncion de Nuestra Señora, Torrelodones.
   - Carta del parroco: empieza con "Queridos feligreses" y termina con "Vuestro Parroco".
   - Imagenes de santos destacados de la semana.

2. **Datos fijos de la parroquia**
   - Apertura de la iglesia.
   - Misas.
   - Confesiones.
   - Exposicion del Santisimo Sacramento.
   - Rosario.
   - Caritas.
   - Charla prebautismal.
   - Despacho parroquial y de cementerio.
   - Equipo pastoral.
   - Direccion, telefonos, email, web y YouTube.

3. **Catecismo de la Iglesia Catolica - Compendio**
   - Encabezados doctrinales: seccion, capitulo y tema.
   - Bloque de preguntas y respuestas.
   - En el numero 1233 aparecen las preguntas 325 a 329.

### Pagina 2

4. **Liturgia dominical**
   - Imagen inicial.
   - Domingo o solemnidad.
   - Lecturas.
   - Salmo.
   - Secuencia, cuando corresponde.
   - Aleluya/aclamacion.
   - Evangelio completo.

5. **Mane nobiscum, Domine**
   - Lema visible sobre la cabecera de Vida Parroquial.
   - Puede funcionar como lema fijo o como frase espiritual semanal.

6. **Vida Parroquial**
   - Avisos breves con casilla.
   - Avisos recurrentes.
   - Carteles o imagenes de actividades.
   - En el ejemplo: apertura, segundos sabados, Monicas, campamento de verano y canal de WhatsApp.

7. **Habla el Papa**
   - Imagen del Papa.
   - Titulo.
   - Extracto breve.
   - En el ejemplo: texto sobre la renovacion de la liturgia.

8. **Nuestro Servicio Informativo**
   - Lista de temas del servicio informativo semanal.
   - Suele tomar contenidos recientes de la web parroquial.

9. **Imagenes y carteles de apoyo**
   - Foto de la parroquia.
   - Imagen liturgica.
   - Santos.
   - Papa.
   - Carteles parroquiales.
   - QR o banners.

## 2. Criterios confirmados

1. **Numero y fecha**
   - El numero de Assumpta sube siempre en 1.
   - La fecha sera siempre la del domingo.

2. **Carta del parroco**
   - El texto se cargara en la app.
   - La app no redactara la carta por defecto.
   - La app ajustara el tamaño para que quepa en su seccion y avisara si el texto es demasiado largo.

3. **Datos fijos**
   - Se actualizan manualmente desde un documento Word cargado en la app.
   - La app extrae el texto del `.docx` y lo ajusta al panel correspondiente.

4. **Compendio**
   - El siguiente numero empieza por la pregunta 330.
   - Se incluiran las preguntas que quepan en el espacio de la seccion.
   - Fuente principal: `Compendio.pdf` local.

5. **Santoral**
   - La app ofrecera santos de la semana.
   - Tu eliges cuales entran en el folleto.
   - La app proporcionara imagenes candidatas para los santos elegidos.

6. **Liturgia dominical**
   - El Evangelio debe proceder de fuente oficial de la Santa Sede/Vaticano.
   - Fuente principal propuesta: Vatican News, seccion "Palabra del dia".
   - La app mostrara siempre la URL de origen y la fecha consultada.
   - Nota importante: Vatican News indica que sus textos proceden del calendario liturgico vaticano y de leccionarios autorizados; la app debe avisar si hay diferencia con el calendario local de España.

7. **Vida Parroquial**
   - Vendrá de un documento Word cargado en la app.
   - La app extraera texto del `.docx` y lo ajustara al espacio disponible.

8. **Habla el Papa**
   - Se usaran Vatican News y Vatican.va.
   - La app propondra contenidos recientes y tu confirmaras el seleccionado.

9. **Servicio Informativo**
   - Se toma por seleccion manual desde un documento Word.
   - La app extrae el texto del `.docx` y lo coloca en la seccion correspondiente.

10. **Imagenes**
    - Para santos: la app debe ofrecer imagenes candidatas junto a cada santo.
    - Pendiente de decidir si hay una carpeta oficial de imagenes parroquiales.

11. **Acceso a la app**
    - Usuario: `pasuntorre`.
    - Contraseña: `pasuntorre26..`.
    - La app pedira estas credenciales al entrar.

12. **Diseño del PDF**
    - Por el momento, el objetivo es replicar el diseño visual exacto del folleto actual.
    - Referencia visual: `1233-Assumpta-07-06-2026.pdf`.

## 3. Preguntas pendientes

1. **Imagenes:** ¿tienes una carpeta oficial de imagenes/logos/carteles que deba usar la app?
2. **Carta:** ¿quieres cargarla pegando texto, subiendo Word, o ambas opciones?
3. **Diseño exacto:** necesito una carpeta con los recursos visuales originales, si existen, para reproducir mejor tipografias, fondos, carteles, santos y logos.

## 4. Fuentes candidatas

- Assumpta historico: https://www.parroquiatorrelodones.com/assumpta/
- Web parroquial y avisos: https://www.parroquiatorrelodones.com/
- RSS parroquial: https://www.parroquiatorrelodones.com/feed/
- Horarios parroquiales: https://www.parroquiatorrelodones.com/horarios/
- Evangelio oficial: https://www.vaticannews.va/es/evangelio-de-hoy/
- Patron por fecha para la app: `https://www.vaticannews.va/es/evangelio-de-hoy/YYYY/MM/DD.html`
- Calendario de la Santa Sede: https://www.vatican.va/content/vatican/es/events.html
- Liturgia auxiliar o comprobacion: https://www.aciprensa.com/calendario/
- Conferencia Episcopal Española: https://www.conferenciaepiscopal.es/
- Archidiocesis de Madrid: https://www.archimadrid.org/
- Vatican News en español: https://www.vaticannews.va/es/papa.html
- Santa Sede: https://www.vatican.va/content/leo-xiv/es.html
- Compendio en Vaticano: https://www.vatican.va/archive/compendium_ccc/documents/archive_2005_compendium-ccc_sp.html
- Santoral: https://www.santopedia.com/santoral/
- Santos ACI Prensa: https://www.aciprensa.com/santos

## 5. Proceso de automatizacion recomendado

1. Abrir la app local.
2. Elegir la fecha del proximo domingo.
3. La app calcula el numero de Assumpta y la pregunta siguiente del Compendio.
4. Cargar la carta del parroco, el Word de Datos Fijos, el Word de Vida Parroquial y el Word del Servicio Informativo.
5. La app consulta Vatican News para el Evangelio y guarda la URL usada.
6. La app lee el Compendio desde la pregunta 330 y añade preguntas hasta llenar la seccion.
7. La app ofrece santos de la semana y sus imagenes para que elijas.
8. La app busca contenidos de "Habla el Papa" en Vatican News y Vatican.va.
9. La app genera un borrador por secciones.
10. Tu revisas y editas carta, datos fijos, vida parroquial, servicio, Papa, santos e imagenes.
11. La app muestra una previsualizacion por panel.
12. Al confirmar, exporta un PDF listo para imprimir como triptico y actualiza el estado semanal.

## 6. Mejoras sugeridas

- Exportar directamente a PDF con plantilla de triptico.
- Medir el espacio disponible por seccion y avisar cuando no quepa.
- Mantener historial de todos los numeros generados.
- Separar contenido fijo, reglas recurrentes y contenido semanal.
- Permitir fuentes manuales de respaldo.
- Añadir vista de revision: borrador, revisado, listo para imprimir.
- Guardar una biblioteca local de imagenes aprobadas.
