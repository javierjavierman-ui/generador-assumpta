# Generador Assumpta

App local para preparar semanalmente la hoja parroquial Assumpta y exportar un PDF en formato triptico.
La version actual usa el PDF `1233-Assumpta-07-06-2026.pdf` como fondo visual para conservar la apariencia del folleto.

## Arranque

```bash
/Users/javiermanuelrodriguezrodriguez/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 app.py
```

Abrir en el navegador:

```text
http://127.0.0.1:5000
```

Si el puerto 5000 esta ocupado, la app usara automaticamente el siguiente disponible entre 5001 y 5009.

## Acceso

- Usuario: `pasuntorre`
- Contraseña: `pasuntorre26..`

## Flujo semanal

1. Indicar la fecha del domingo.
2. Confirmar el numero de Assumpta.
3. Cargar o pegar la carta del parroco, o dejarla vacia para que la app proponga un borrador.
4. Revisar el Catecismo, que se rellena automaticamente desde el Compendio.
5. Revisar Evangelio, lecturas, cargar Secuencia desde Word si corresponde, y revisar imagen liturgica.
6. Cargar el Word o pegar el texto del anuncio central. Si se desea, cargar tambien una imagen para que aparezca encima del texto.
7. Cargar el Word de "Habla el Papa".
8. Elegir uno o dos santos.
9. Pulsar "Previsualizar triptico".
10. Revisar las dos paginas completas.
11. Abrir el PDF final y, si es correcto, marcar "Actualizar estado".

## Reglas incorporadas

- El numero sube siempre en 1.
- La fecha es la del domingo.
- El Compendio continua por la pregunta 330 y añade las preguntas que caben.
- El Compendio incluye el encabezado doctrinal fijo de la Segunda Seccion antes de las preguntas.
- Los datos fijos, avisos fijos, pie central, imagen superior del Papa y Servicio Informativo quedan congelados desde la plantilla visual.
- El anuncio central se carga desde Word, texto pegado e imagen opcional. Si hay texto e imagen, la imagen queda arriba y el texto debajo.
- "Habla el Papa" se carga desde Word.
- El Evangelio se consulta en Vatican News, seccion "Palabra del dia".
- El Aleluya completo es fijo y se imprime antes del Evangelio.
- La app añade automaticamente el titulo "Santo Evangelio segun..." a partir de la referencia.
- La app ofrece santos de la semana para elegir y descarga imagenes automaticamente cuando puede.
- El PDF se genera escribiendo solo encima de los huecos variables del folleto original.

## Nota sobre el Evangelio

Vatican News es una fuente del Dicasterio para la Comunicacion de la Santa Sede. Su seccion "Palabra del dia" indica que propone lecturas segun el calendario liturgico vaticano. La app conserva la URL usada y avisa si conviene comparar con el calendario local de España.

## Mostrar la app a otras personas

Para una demostracion con URL temporal:

```bash
sh compartir_app.sh
```

La app pedira las mismas credenciales:

- Usuario: `pasuntorre`
- Contraseña: `pasuntorre26..`

La URL temporal funcionara mientras el ordenador este encendido y la ventana del tunel siga abierta. Si aparece el aviso `No se encontro cloudflared`, hay que instalar Cloudflare Tunnel antes de compartir la app.
