# Pulso Cashless · Tablero de operación de eventos + agente de voz (ElevenLabs)

Proyecto académico: tablero interactivo en HTML sobre la operación de eventos con pagos cashless (pulseras NFC), con un agente de ElevenLabs (voz y texto) incrustado cuyo conocimiento (RAG) es el contenido del propio tablero.

> **Todos los datos son simulados.** "Pulso Cashless" es una empresa ficticia; los 16 eventos y sus cifras se generan con `generar_datos.py` (semilla 42).

- **Tablero (GitHub Pages):** https://jpcamfer-design.github.io/pulso-cashless-dashboard/
- **Agente en ElevenLabs (liga directa):** https://elevenlabs.io/app/talk-to?agent_id=agent_8301m6786zgxe6r95zpy36jq6n48

## Qué incluye el tablero
- KPIs filtrables por tipo de evento, ciudad y evento.
- Hallazgos que se recalculan con los filtros, etiquetados como Observado / Inferencia / Supuesto, con acción e indicador de seguimiento.
- 9 gráficas: ventas, gasto por pulsera, carga vs. fila (recta ajustada), fila vs. gasto, hora pico, incidentes de terminal, saldo no usado, medios de recarga y categorías.
- Calculadora de dimensionamiento (estaciones de recarga, terminales, staff, ventas esperadas).
- Tabla ordenable, guía de operación cashless, metodología y límites.
- Widget del agente de ElevenLabs (voz + chat).

## Agente
| Parámetro | Valor |
|---|---|
| Nombre | Pulso · Asistente del tablero cashless |
| Idioma / voz | Español · Marto (español mexicano) |
| LLM | Claude Haiku 5.5, temperatura mínima |
| Conocimiento | `kb_pulso_tablero.md` (mismo contenido y cifras que el HTML) |
| Recuperación | RAG en cada turno, embeddings multilingües |
| Regla clave | Responde solo con el tablero; si no está, dice "Esa información no está en el tablero." |

## Reproducir
```bash
python3 generar_datos.py   # data.json (semilla 42)
python3 generar_kb.py      # kb_pulso_tablero.md
python3 build.py           # index.html = template.html + data.json
```

## Archivos
- `index.html` — tablero publicado (autocontenido; Chart.js y el widget se cargan por CDN).
- `template.html` — plantilla del tablero; `build.py` le inyecta los datos.
- `data.json` — dataset simulado.
- `generar_datos.py`, `generar_kb.py` — simulador y generador de la base de conocimiento.
- `kb_pulso_tablero.md` — documento cargado al agente.
