# 🐾 Fichas Veterinarias

Una veterinaria atiende decenas de pacientes por semana. Cada consulta termina en una ficha manuscrita: el nombre del animal, su peso, los análisis de sangre, los cálculos de RER y RED, la dieta indicada con gramajes exactos, los suplementos, la fecha del próximo control. Esa información existe, pero está atrapada en papel.

Este proyecto la libera.

---

## El problema

Las fichas clínicas veterinarias manuscritas son difíciles de sistematizar. Tienen estructura variable, abreviaturas específicas del campo (RER, RED, PB, EE, Hto, GPT, GOT), números dispersos entre texto, y letra que varía de profesional en profesional. Las soluciones tradicionales de OCR —Tesseract, por ejemplo— fallan con manuscritos. Transcribir a mano es lento y propenso a errores.

El resultado es que los datos existen pero no se pueden analizar: no hay manera fácil de saber cuántos pacientes tienen sobrepeso, qué dietas se prescriben más, o cuándo vence el próximo control de cada animal.

---

## La solución

Una aplicación web que toma un PDF escaneado de una ficha veterinaria y devuelve los datos estructurados en una base de datos, listos para consultar, exportar y analizar.

El flujo completo:

**1. El usuario sube la ficha** — arrastrando el PDF al dashboard o seleccionando varios archivos de una vez. La app acepta PDFs de múltiples páginas e imágenes JPG/PNG.

**2. El OCR corre en background** — sin bloquear la interfaz. La ficha aparece en la lista con estado "procesando" y cambia a "listo" en segundos, sin necesidad de recargar la página.

**3. Claude Vision lee el manuscrito** — no como un OCR tradicional que transcribe caracteres, sino como un lector que entiende el contexto. Sabe que "3,5 x 1,2 = 195" es un cálculo de RED, que "Hto 53 GB 3600" son valores de hemograma, que "350g pollo + 200g batata + 15g aceite" es una prescripción dietaria. Extrae 27 campos estructurados de cada ficha.

**4. El profesional revisa** — ve la imagen original al lado del formulario con los datos extraídos. Corrige lo que el OCR no leyó bien. Guarda. Los datos quedan en la base de datos.

**5. Los datos se pueden exportar** — en cualquier momento, un botón descarga todas las fichas (o las filtradas por búsqueda) como CSV compatible con Excel.

---

## Qué información extrae de cada ficha

De una ficha típica como esta:

```
ADRIANA BARRACO          12/5/25
ROGER — pastor australiano ♂ 4 años — 19,7kg
bajo peso (alérgico a BDF)
Hto 53  GB 3600  Ur 44  GPT 70  GOT 64  FAS 30  Co 7,66
RED: 24 x 1,8 = 1366 kcal
PB: 50,96–81,32   EE: 19,5–114   Co 1,41   P 1,08
460g carne + 250g verdura + 350g fideos + 20g aceite
+ 2 TTD + 15g yogur
Control 30d. Pesar en 15d.
```

La app construye automáticamente este registro:

| Campo | Valor extraído |
|-------|---------------|
| Propietario | Barraco, Adriana |
| Paciente | Roger |
| Especie / Raza | Canino, Pastor Australiano |
| Sexo | Macho |
| Edad | 4 años |
| Peso actual | 19,7 kg |
| Fecha de consulta | 12/05/25 |
| Motivo | Bajo peso, alérgico a BDF |
| Análisis clínicos | Hto 53, GB 3600, Ur 44, GPT 70, GOT 64, FAS 30, Co 7,66 |
| RED | 1366 kcal/día |
| Factor RED | 1,8 |
| PB mín / máx | 50,96 — 81,32 g |
| EE mín / máx | 19,5 — 114 g |
| Co | 1,41 g |
| P | 1,08 g |
| Dieta | 460g carne + 250g verdura + 350g fideos + 20g aceite + 2 TTD + 15g yogur |
| Suplementos | TTD, Co |
| Control | 30 días |
| Notas | Pesar en 15 días |

---

## Lo que el profesional puede hacer con esos datos

Una vez que las fichas están digitalizadas:

- **Buscar** por propietario, paciente, especie o diagnóstico
- **Filtrar** por estado de procesamiento
- **Corregir** cualquier campo desde la interfaz, con la imagen original visible al lado
- **Exportar** todo a CSV para análisis en Excel, Google Sheets o cualquier herramienta estadística
- **Acceder al historial** de cada paciente desde cualquier dispositivo con browser
- **Volver a procesar** fichas que fallaron o que quieran re-analizar

Lo que antes requería transcripción manual ahora tarda segundos por ficha.

---

## El backend de OCR es intercambiable

La app soporta dos motores de extracción:

**Claude Vision (Anthropic)** — es la opción por defecto y la más precisa para este tipo de documento. Entiende el español médico-veterinario, maneja la variabilidad de la letra manuscrita, y reconoce los cálculos y abreviaturas propias del campo. El costo es aproximadamente $8–12 USD para procesar 800 fichas con el modelo Sonnet.

**Ollama (local)** — para quien tenga GPUs disponibles y prefiera no depender de una API externa. Corre completamente en la infraestructura propia, sin costo por request. La calidad es menor que Claude para abreviaturas clínicas específicas, pero suficiente para fichas con letra clara. Se configura con una línea en el archivo `.env`.

Cambiar de uno a otro no requiere modificar código, solo la variable `OCR_BACKEND`.

---

## Stack técnico

- **Django** como framework web y ORM
- **SQLite** en desarrollo y despliegues pequeños — **PostgreSQL** para producción a escala
- **pdf2image + poppler** para convertir PDFs a imágenes antes de enviárselas al modelo de visión
- **Whitenoise** para servir archivos estáticos sin necesidad de Nginx en deployments simples
- **Docker** para el empaquetado y deploy
- **Railway** como plataforma de hosting — incluye SSL automático con Let's Encrypt

---

## Estado del proyecto

La app procesa fichas, las almacena y las exporta. Lo que viene:

- [ ] Historial de consultas por paciente (múltiples fichas del mismo animal)
- [ ] Gráficos de evolución de peso y parámetros clínicos
- [ ] Alertas de control próximo (pacientes con control vencido)
- [ ] API REST para integración con otros sistemas
- [ ] Soporte para procesar fichas en lote desde línea de comandos

---

## Documentación técnica

Para instrucciones de instalación local, configuración de variables de entorno, opciones de deploy y setup de Ollama, ver el [README técnico](README_tecnico.md).
