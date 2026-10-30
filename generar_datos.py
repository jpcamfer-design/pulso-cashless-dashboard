"""
Genera el dataset SIMULADO de eventos cashless para el dashboard y la base de
conocimiento (RAG) del agente. Semilla fija => mismo resultado siempre, así las
cifras del HTML y las del documento de conocimiento coinciden exactamente.

Todo es ficticio: empresa, eventos, cifras. Las relaciones (p.ej. fila -> gasto)
son SUPUESTOS de la simulación, no evidencia empírica.
"""
import json
import numpy as np

rng = np.random.default_rng(42)

# ---------------------------------------------------------------- supuestos
TIPOS = {
    # act: tasa de activación de pulseras; gasto: MXN por pulsera activada (base)
    # ticket: MXN por transacción; unused: % recargas no consumido
    # rech_pp: recargas por persona; ratio_est: asistentes por estación de recarga (rango)
    # ratio_term: pulseras activadas por terminal de venta (rango)
    # horas: ventana de operación (hora inicio, hora fin, hora pico, dispersión)
    "Festival":   dict(act=.93, gasto=780, ticket=165, unused=.07, rech_pp=1.8,
                       ratio_est=(1400, 3600), ratio_term=(110, 190),
                       metodo=dict(Tarjeta=.55, Efectivo=.18, Online=.27, Cortesia=0),
                       cat=dict(Bebidas=.58, Alimentos=.27, Merch=.10, Otros=.05),
                       horas=(13, 24, 21.0, 2.6)),
    "Concierto":  dict(act=.88, gasto=520, ticket=140, unused=.09, rech_pp=1.4,
                       ratio_est=(550, 1400), ratio_term=(90, 170),
                       metodo=dict(Tarjeta=.50, Efectivo=.24, Online=.26, Cortesia=0),
                       cat=dict(Bebidas=.62, Alimentos=.22, Merch=.12, Otros=.04),
                       horas=(17, 24, 20.5, 1.6)),
    "Escuela":    dict(act=.76, gasto=160, ticket=45, unused=.04, rech_pp=1.3,
                       ratio_est=(350, 900), ratio_term=(45, 90),
                       metodo=dict(Tarjeta=.20, Efectivo=.70, Online=.10, Cortesia=0),
                       cat=dict(Bebidas=.25, Alimentos=.60, Merch=.05, Otros=.10),
                       horas=(9, 16, 12.5, 1.5)),
    "Activación": dict(act=.97, gasto=220, ticket=70, unused=.18, rech_pp=1.1,
                       ratio_est=(300, 800), ratio_term=(40, 80),
                       metodo=dict(Tarjeta=.25, Efectivo=.08, Online=.12, Cortesia=.55),
                       cat=dict(Bebidas=.45, Alimentos=.35, Merch=.15, Otros=.05),
                       horas=(11, 20, 15.5, 2.0)),
}
COMISION = 0.045        # % sobre ventas que cobra la plataforma (supuesto)
FEE_PULSERA = 15        # MXN por pulsera activada (supuesto)
UMBRAL_FILA = 6         # min, objetivo operativo de fila en recarga (supuesto)

EVENTOS = [
    # id, nombre, tipo, ciudad, fecha, dias, asistentes
    ("E01", "Festival Aurora",          "Festival",   "CDMX",        "2026-02-14", 2, 52000),
    ("E02", "Noche Retro 90s",          "Concierto",  "CDMX",        "2026-02-28", 1, 14500),
    ("E03", "Kermés Colegio Alameda",   "Escuela",    "Naucalpan",   "2026-03-07", 1, 2300),
    ("E04", "Lanzamiento Bebida Zeta",  "Activación", "CDMX",        "2026-03-19", 1, 1800),
    ("E05", "Festival Sierra Sonora",   "Festival",   "Monterrey",   "2026-04-04", 2, 41000),
    ("E06", "Gira Eclipse",             "Concierto",  "Guadalajara", "2026-04-18", 1, 18200),
    ("E07", "Feria Día del Niño",       "Escuela",    "Querétaro",   "2026-04-30", 1, 3600),
    ("E08", "Pop-up Tenis Urbano",      "Activación", "Monterrey",   "2026-05-16", 1, 1200),
    ("E09", "Concierto Sinfónico Rock", "Concierto",  "Puebla",      "2026-05-30", 1, 9800),
    ("E10", "Festival Marea",           "Festival",   "Guadalajara", "2026-06-20", 2, 36500),
    ("E11", "Graduación Prepa Lomas",   "Escuela",    "CDMX",        "2026-07-03", 1, 1600),
    ("E12", "Noche Reguetón Norte",     "Concierto",  "Monterrey",   "2026-07-25", 1, 16800),
    ("E13", "Festival Vértice",         "Festival",   "CDMX",        "2026-08-22", 3, 61000),
    ("E14", "Activación Café Altura",   "Activación", "Querétaro",   "2026-09-05", 1, 2600),
    ("E15", "Feria Patria Escolar",     "Escuela",    "Puebla",      "2026-09-15", 1, 2900),
    ("E16", "Tributo Leyendas",         "Concierto",  "CDMX",        "2026-10-10", 1, 12400),
]


def norm(d):
    s = sum(d.values())
    return {k: v / s for k, v in d.items()}


def jitter_mix(mix, sd=.03):
    out = {k: (max(0.0, v + rng.normal(0, sd)) if v > 0 else 0.0) for k, v in mix.items()}
    return norm(out)


eventos, horario = [], {}
for eid, nombre, tipo, ciudad, fecha, dias, asis in EVENTOS:
    p = TIPOS[tipo]
    h0, h1, pico, disp = p["horas"]
    horas_dia = h1 - h0
    horas_op = horas_dia * dias

    activadas = int(round(asis * np.clip(p["act"] + rng.normal(0, .025), .6, .995)))
    estaciones = max(2, int(round(asis / rng.uniform(*p["ratio_est"]))))
    terminales = max(4, int(round(activadas / rng.uniform(*p["ratio_term"]))))

    # Carga = personas activadas por estación por hora de operación
    carga = activadas / (estaciones * horas_op)
    fila = max(1.0, (1.2 + 0.075 * carga) * rng.normal(1, .12) + rng.normal(0, .5))

    # SUPUESTO de simulación: cada minuto de fila por encima de 5 min reduce 2.5% el gasto (tope 30%)
    penal = 1 - min(.30, 0.025 * max(0.0, fila - 5))
    gasto_pp = p["gasto"] * penal * rng.normal(1, .06)
    ventas = activadas * gasto_pp

    unused_pct = float(np.clip(p["unused"] + rng.normal(0, .012), .015, .3))
    recargas = ventas / (1 - unused_pct)
    saldo_no_usado = recargas - ventas
    reemb_pct = float(np.clip(rng.normal(.45, .08), .25, .7))
    reembolsos = saldo_no_usado * reemb_pct

    ticket = p["ticket"] * rng.normal(1, .05)
    transacciones = int(round(ventas / ticket))
    n_recargas = int(round(activadas * p["rech_pp"] * rng.normal(1, .05)))

    metodo = jitter_mix(p["metodo"])
    cat = jitter_mix(p["cat"])

    incidentes = int(rng.poisson(terminales * .035 * dias))
    uptime = float(np.clip(99.85 - incidentes / terminales * 18 + rng.normal(0, .15), 95, 99.95))
    tx_seg = float(np.clip(rng.normal(7.2, .9), 5, 11))
    staff = int(round(estaciones * 3 + terminales * 1.1 + rng.normal(0, 3)))

    ingreso_plat = ventas * COMISION + activadas * FEE_PULSERA

    # Curva horaria (transacciones por hora de reloj, sumando todos los días)
    hrs = list(range(h0, h1))
    pico_e = pico + rng.normal(0, .7)
    w = np.exp(-0.5 * ((np.array(hrs) + .5 - pico_e) / disp) ** 2)
    w = w / w.sum()
    tx_h = np.round(w * transacciones).astype(int)
    tx_h[-1] += transacciones - tx_h.sum()  # cuadrar el total exacto
    horario[eid] = dict(horas=[f"{h:02d}:00" for h in hrs], tx=tx_h.tolist())

    eventos.append(dict(
        id=eid, nombre=nombre, tipo=tipo, ciudad=ciudad, fecha=fecha, dias=dias,
        horas_op=horas_op, asistentes=asis, pulseras=activadas,
        estaciones=estaciones, terminales=terminales, staff=staff,
        recargas=round(recargas), n_recargas=n_recargas,
        ventas=round(ventas), transacciones=transacciones,
        ticket=round(ventas / transacciones, 1),
        gasto_pp=round(ventas / activadas, 1),
        saldo_no_usado=round(saldo_no_usado), reembolsos=round(reembolsos),
        breakage=round(saldo_no_usado - reembolsos),
        fila_min=round(fila, 1), carga=round(carga, 1),
        incidentes=incidentes, uptime=round(uptime, 2), tx_seg=round(tx_seg, 1),
        ingreso_plat=round(ingreso_plat),
        metodo={k: round(v, 4) for k, v in metodo.items()},
        cat={k: round(v, 4) for k, v in cat.items()},
        pico=horario[eid]["horas"][int(np.argmax(tx_h))],
    ))

# ----------------------------------------- modelo simple fila ~ carga (OLS)
x = np.array([e["carga"] for e in eventos])
y = np.array([e["fila_min"] for e in eventos])
b, a = np.polyfit(x, y, 1)
yhat = a + b * x
r2 = 1 - ((y - yhat) ** 2).sum() / ((y - y.mean()) ** 2).sum()
carga_max = (UMBRAL_FILA - a) / b

# correlación fila vs gasto relativo al promedio de su tipo
rel = []
for e in eventos:
    base = np.mean([f["gasto_pp"] for f in eventos if f["tipo"] == e["tipo"]])
    rel.append(e["gasto_pp"] / base)
r_fila_gasto = float(np.corrcoef(y, rel)[0, 1])

data = dict(
    meta=dict(
        empresa="Pulso Cashless (empresa ficticia)",
        periodo="ene–oct 2026",
        moneda="MXN",
        semilla=42,
        nota="Datos 100% simulados con fines académicos. Las relaciones entre variables son supuestos del simulador.",
        supuestos=dict(comision=COMISION, fee_pulsera=FEE_PULSERA, umbral_fila=UMBRAL_FILA),
    ),
    eventos=eventos,
    horario=horario,
    modelo=dict(a=round(float(a), 3), b=round(float(b), 4), r2=round(float(r2), 3),
                n=len(eventos), carga_max=round(float(carga_max), 1),
                r_fila_gasto=round(r_fila_gasto, 2)),
)

with open("data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=1)

print(f"OK {len(eventos)} eventos | fila = {a:.2f} + {b:.4f}*carga | R2={r2:.3f} | "
      f"carga_max@{UMBRAL_FILA}min={carga_max:.1f} | r(fila,gasto_rel)={r_fila_gasto:.2f}")
for e in eventos:
    print(e["id"], e["tipo"][:5], e["asistentes"], e["estaciones"], e["carga"], e["fila_min"],
          e["gasto_pp"], e["ventas"], e["uptime"], e["pico"])
