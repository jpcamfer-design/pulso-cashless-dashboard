"""
Genera la base de conocimiento del chat del tablero (kb_tablero.md) con las MISMAS
cifras que muestra index.html (mismas fórmulas que el JavaScript del tablero).
"""
import json, math
from statistics import median

D = json.load(open("data.json", encoding="utf-8"))
EV, M, S = D["eventos"], D["modelo"], D["meta"]["supuestos"]
TIPOS = ["Festival", "Concierto", "Escuela", "Activación"]


def agg(es):
    v = sum(e["ventas"] for e in es); p = sum(e["pulseras"] for e in es); a = sum(e["asistentes"] for e in es)
    r = sum(e["recargas"] for e in es); su = sum(e["saldo_no_usado"] for e in es); br = sum(e["breakage"] for e in es)
    tx = sum(e["transacciones"] for e in es); t = sum(e["terminales"] for e in es)
    return dict(n=len(es), ventas=v, pulseras=p, asis=a, rec=r, su=su, br=br, tx=tx, term=t,
                act=p / a, gasto=v / p, ticket=v / tx, su_pct=su / r,
                fila=sum(e["fila_min"] for e in es) / len(es),
                uptime=sum(e["uptime"] * e["terminales"] for e in es) / t,
                inc=sum(e["incidentes"] for e in es), ingreso=sum(e["ingreso_plat"] for e in es))


def m(x):  # formato dinero
    if abs(x) >= 1e6: return f"${x/1e6:,.1f} M"
    if abs(x) >= 1e3: return f"${x/1e3:,.0f} mil"
    return f"${x:,.0f}"


def pc(x, d=1): return f"{x*100:.{d}f}%"


g = agg(EV)
L = []
w = L.append
w("# Base de conocimiento — Tablero Pulso Cashless (contenido del HTML)")
w("")
w("Este documento contiene exactamente la información que muestra el tablero web. "
  "Todas las cifras son SIMULADAS con fines académicos (empresa ficticia “Pulso Cashless”, 16 eventos, enero a octubre de 2026, pesos mexicanos MXN). "
  "No representan a ninguna empresa real.")
w("")
w("## 1. Indicadores generales (16 eventos)")
w(f"- Ventas brutas: {m(g['ventas'])} (exacto ${g['ventas']:,} MXN).")
w(f"- Asistentes: {g['asis']:,}. Pulseras activadas: {g['pulseras']:,}. Tasa de activación: {pc(g['act'])}.")
w(f"- Gasto por pulsera activada: ${g['gasto']:,.0f} MXN. Ticket promedio: ${g['ticket']:,.0f} MXN. Transacciones: {g['tx']:,}.")
w(f"- Recargas totales: {m(g['rec'])}. Saldo no usado: {m(g['su'])} ({pc(g['su_pct'])} de lo recargado). "
  f"Breakage neto (no reembolsado): {m(g['br'])} ({pc(g['br']/g['rec'])} de las recargas).")
w(f"- Fila promedio en estación de recarga: {g['fila']:.1f} minutos (promedio simple por evento). Objetivo operativo: {S['umbral_fila']} minutos o menos.")
w(f"- Uptime de terminales (ponderado por terminales): {g['uptime']:.2f}%. Incidentes de terminal: {g['inc']} en {g['term']:,} terminales desplegadas.")
w(f"- Ingreso estimado de la plataforma: {m(g['ingreso'])} (supuesto comercial: comisión de 4.5% sobre ventas más $15 MXN por pulsera activada).")
w("")
w("## 2. Indicadores por tipo de evento")
for t in TIPOS:
    es = [e for e in EV if e["tipo"] == t]; a = agg(es)
    mr = [sum(e["recargas"] * e["metodo"][k] for e in es) / a["rec"] for k in ["Tarjeta", "Efectivo", "Online", "Cortesia"]]
    mc = [sum(e["ventas"] * e["cat"][k] for e in es) / a["ventas"] for k in ["Bebidas", "Alimentos", "Merch", "Otros"]]
    nom = "Activación de marca" if t == "Activación" else t
    cort = "cortesía de marca" if t == "Activación" else "cortesía"
    w(f"- {nom}: {a['n']} eventos; {a['asis']:,} asistentes; ventas {m(a['ventas'])} ({pc(a['ventas']/g['ventas'])} del total); activación {pc(a['act'])}; "
      f"gasto por pulsera ${a['gasto']:,.0f}; ticket ${a['ticket']:,.0f}; saldo no usado {pc(a['su_pct'])}; fila promedio {a['fila']:.1f} min; uptime {a['uptime']:.2f}%; "
      f"mezcla de recarga: tarjeta {pc(mr[0],0)}, efectivo {pc(mr[1],0)}, en línea {pc(mr[2],0)}, {cort} {pc(mr[3],0)}; "
      f"mezcla de ventas: bebidas {pc(mc[0],0)}, alimentos {pc(mc[1],0)}, merch {pc(mc[2],0)}, otros {pc(mc[3],0)}.")
w("")
w("## 3. Detalle por evento")
w("Carga = pulseras activadas ÷ (estaciones de recarga × horas de operación). Índice de gasto = gasto por pulsera ÷ promedio ponderado de su tipo × 100.")
w("")
gt = {t: sum(e["ventas"] for e in EV if e["tipo"] == t) / sum(e["pulseras"] for e in EV if e["tipo"] == t) for t in TIPOS}
for e in sorted(EV, key=lambda x: -x["ventas"]):
    w(f"- {e['nombre']} ({e['tipo']}, {e['ciudad']}, {e['fecha']}, {e['dias']} día{'s' if e['dias']>1 else ''}): asistentes {e['asistentes']:,}; pulseras activadas {e['pulseras']:,}; "
      f"ventas ${e['ventas']:,} MXN; gasto por pulsera ${e['gasto_pp']:,.0f}; ticket promedio ${e['ticket']:,.0f}; índice de gasto {e['gasto_pp']/gt[e['tipo']]*100:.0f}; "
      f"estaciones de recarga {e['estaciones']}; terminales {e['terminales']}; staff {e['staff']}; carga {e['carga']:.1f} personas por estación por hora; "
      f"fila promedio en recarga {e['fila_min']:.1f} min{' (arriba del objetivo de 6 min)' if e['fila_min']>S['umbral_fila'] else ' (dentro del objetivo)'}; "
      f"saldo no usado {pc(e['saldo_no_usado']/e['recargas'])} de lo recargado, del cual se reembolsó {pc(e['reembolsos']/e['saldo_no_usado'],0)}; breakage ${e['breakage']:,} MXN; "
      f"incidentes de terminal {e['incidentes']} ({e['incidentes']/e['terminales']*100:.1f} por cada 100 terminales); uptime {e['uptime']:.2f}%; hora pico {e['pico']}.")
w("")
w("## 4. Rankings")
def rk(titulo, key, fmt, rev=True, n=3):
    s = sorted(EV, key=lambda e: key(e), reverse=rev)[:n]
    w(f"- {titulo}: " + "; ".join(f"{i+1}) {e['nombre']} ({fmt(key(e))})" for i, e in enumerate(s)) + ".")
rk("Mayores ventas", lambda e: e["ventas"], m)
rk("Mayor gasto por pulsera", lambda e: e["gasto_pp"], lambda x: f"${x:,.0f}")
rk("Fila más larga", lambda e: e["fila_min"], lambda x: f"{x:.1f} min")
rk("Fila más corta", lambda e: e["fila_min"], lambda x: f"{x:.1f} min", rev=False)
rk("Mayor % de saldo no usado", lambda e: e["saldo_no_usado"] / e["recargas"], pc)
rk("Más incidentes por 100 terminales", lambda e: e["incidentes"] / e["terminales"] * 100, lambda x: f"{x:.1f}")
w("")
w("## 5. Modelo de filas y hallazgos")
sobre = [e for e in EV if e["fila_min"] > S["umbral_fila"]]
falt = sum(max(0, math.ceil(e["pulseras"] / (M["carga_max"] * e["horas_op"])) - e["estaciones"]) for e in sobre)
top3 = sorted(EV, key=lambda e: -e["ventas"])[:3]
w(f"- Recta ajustada con los 16 eventos: fila (min) = {M['a']} + {M['b']} × carga. R² = {M['r2']}. "
  f"Para una fila de {S['umbral_fila']} min o menos, la carga debe ser como máximo {M['carga_max']} personas por estación por hora. "
  f"Es una inferencia sobre datos simulados y solo es confiable dentro del rango de carga observado ({min(e['carga'] for e in EV):.0f} a {max(e['carga'] for e in EV):.0f}).")
w(f"- {len(sobre)} de 16 eventos superaron la fila objetivo de {S['umbral_fila']} min; con la recta, en esos eventos faltaron aproximadamente {falt} estaciones de recarga en total.")
w(f"- Concentración: los 3 eventos con más ventas ({', '.join(e['nombre'] for e in top3)}) suman {pc(sum(e['ventas'] for e in top3)/g['ventas'],0)} de las ventas.")
w(f"- Correlación entre fila e índice de gasto: r = {M['r_fila_gasto']}. Los eventos con más fila gastan menos que el promedio de su tipo. "
  "IMPORTANTE: esta relación fue programada en el simulador (−2.5% de gasto por cada minuto de fila arriba de 5 min, tope 30%); es una hipótesis, no una causa probada.")
w("- Las activaciones de marca tienen el mayor saldo sin usar porque una parte de las recargas es cortesía de la marca.")
w("- En escuelas domina el efectivo como medio de recarga; en festivales y conciertos domina la tarjeta.")
w("- En escuelas la categoría principal es alimentos; en los demás tipos, bebidas.")
w("- Horas pico típicas: escuelas alrededor de las 12:00, activaciones alrededor de las 14:00–15:00, conciertos y festivales entre 19:00 y 21:00.")
w("")
w("## 6. Calculadora de dimensionamiento (cómo funciona)")
w("La calculadora del tablero estima, para un tipo de evento, asistentes esperados, días y fila objetivo:")
w("- Pulseras esperadas = asistentes × tasa de activación promedio del tipo.")
w(f"- Estaciones de recarga = pulseras ÷ (carga máxima para la fila objetivo × horas de operación). Carga máxima = (fila objetivo − {M['a']}) ÷ {M['b']}, con la recta de la sección 5. Para fila de 6 min, carga máxima {M['carga_max']}.")
w("- Terminales de venta = pulseras ÷ mediana de pulseras por terminal del tipo × 1.05 (5% de respaldo).")
w("- Staff estimado = 3 por estación de recarga + 1.1 por terminal.")
w("- Ventas esperadas = pulseras × rango (mínimo a máximo) de gasto por pulsera observado en el tipo.")
w("Referencias por tipo:")
for t in TIPOS:
    es = [e for e in EV if e["tipo"] == t]
    hd = median([e["horas_op"] / e["dias"] for e in es]); act = sum(e["pulseras"] for e in es) / sum(e["asistentes"] for e in es)
    w(f"- {t}: activación {pc(act)}, {hd:.0f} horas de operación por día, mediana de {median([e['pulseras']/e['terminales'] for e in es]):.0f} pulseras por terminal, "
      f"gasto por pulsera de ${min(e['gasto_pp'] for e in es):,.0f} a ${max(e['gasto_pp'] for e in es):,.0f}.")
es=[e for e in EV if e["tipo"]=="Concierto"]; act=sum(e["pulseras"] for e in es)/sum(e["asistentes"] for e in es)
P=20000*act; hrs=median([e["horas_op"]/e["dias"] for e in es]); cm=(6-M["a"])/M["b"]; est=math.ceil(P/(cm*hrs))
term=math.ceil(P/median([e["pulseras"]/e["terminales"] for e in es])*1.05); gs=[e["gasto_pp"] for e in es]
w(f"Ejemplo de la calculadora: concierto de 20,000 asistentes, 1 día, fila objetivo de 6 min → {P:,.0f} pulseras esperadas, {est} estaciones de recarga, {term} terminales, {round(est*3+term*1.1)} personas de staff y ventas esperadas de {m(P*min(gs))} a {m(P*max(gs))}.")
w("")
w("## 7. Guía de operación cashless (sección del tablero)")
w("Cómo funciona: el asistente recibe una pulsera o tarjeta NFC; se activa al registrarla o cargarle saldo. Recarga saldo antes o durante el evento y paga acercando la pulsera a una terminal. El efectivo solo se recibe en las estaciones de recarga, nunca en barras ni puestos. Ventajas: cobro más rápido, menos manejo de caja y datos de venta en tiempo real por punto, hora y producto. Riesgos: conectividad y batería de terminales, filas en recarga y saldo no consumido.")
w("Ciclo de un evento: (1) Planeación: asistentes, tipo, horario, puntos de venta y dimensionamiento con la calculadora. (2) Montaje: pruebas de red, catálogo cargado, baterías al 100% y 5% de terminales de respaldo. (3) Capacitación del staff del cliente: cobrar, revisar saldo y reportar fallas. (4) Operación: estaciones de recarga abiertas 1 hora antes de abrir puertas; refuerzo de staff 1 hora antes de la hora pico. (5) Cierre: arqueo de efectivo, conciliación por punto de venta y conteo de terminales. (6) Postevento: reembolsos y reporte al cliente.")
w("Recargas y reembolsos (política de ejemplo): medios de recarga: tarjeta, efectivo, recarga en línea previa y cortesía de marca. Recarga mínima $100 MXN; montos sugeridos $200, $500 y $1,000. Reembolso del saldo no usado durante 15 días después del evento, con comisión de $15 MXN. La cortesía de marca no es reembolsable. El destino del breakage se pacta en el contrato con el organizador. En escuelas: cajeros con fondo fijo y arqueos parciales cada 2 horas.")
w("Terminales e incidentes: fallas comunes: batería baja, sin señal, lector NFC que no responde y catálogo sin sincronizar. Protocolo: reiniciar, cambiar a red de respaldo, cambiar por terminal de respaldo y registrar hora, punto de venta y causa. Indicadores: uptime, incidentes por 100 terminales y tiempo medio de reparación (MTTR). Modo sin conexión: la terminal sigue cobrando y sincroniza después; el saldo mostrado puede desfasarse. Pulsera perdida: si está registrada, se bloquea y el saldo pasa a una pulsera nueva.")
w("")
w("## 8. Metodología, glosario y límites")
w("- Fórmulas: activación = pulseras ÷ asistentes; gasto por pulsera = ventas ÷ pulseras; ticket = ventas ÷ transacciones; saldo no usado = recargas − ventas; breakage = saldo no usado − reembolsos; uptime ponderado por terminales.")
w("- Cashless: el asistente paga con pulsera o tarjeta NFC precargada. Estación de recarga: punto donde se carga saldo. Terminal: equipo de cobro en barras y puestos. Breakage: saldo recargado que nadie consume ni reclama. Uptime: % del tiempo en que la terminal funcionó.")
w("- Lo que NO se puede afirmar con estos datos: causalidad entre fila y gasto; comparaciones robustas entre tipos (solo 3 a 5 eventos por tipo, n = 16); márgenes de los vendedores; costos de operación; satisfacción del asistente; la fila en el minuto pico (solo hay promedio por evento).")

open("kb_pulso_tablero.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
print("kb_pulso_tablero.md:", len("\n".join(L)), "caracteres")
print(f"check: ventas {g['ventas']} fila {g['fila']:.2f} uptime {g['uptime']:.4f} gasto {g['gasto']:.2f} faltan {falt} sobre {len(sobre)}")
