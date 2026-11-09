"""
EdiHub em Ação: o pico de acessos antes do fim das inscrições
==============================================================
Global Solution 2026.2 · CitizenTech · Differentiated Problem Solving (FIAP)

Equipe:
    Bernardo de Paula Rodrigues - RM 572376
    Arthur Moreira Costa        - RM 571532
    Henrique Nunes Mororó       - RM 574073

Modelo:  A(t) = t^4 · e^(-t/7)      (acessos por dia ao edital)
         t = dias desde a abertura das inscrições (prazo fecha no dia 30)

Como usar:
    1) python edihub_calculo.py
       -> mostra a análise no terminal e gera o arquivo index.html
    2) Suba a pasta com o index.html na Vercel (arrastar e soltar ou `vercel deploy`).

Só usa a biblioteca padrão do Python (math e json). O gráfico é desenhado
no navegador com Plotly.js, a partir dos números calculados aqui.
"""

import json
import math

# ---------------------------------------------------------------------------
# 1. PARÂMETROS DO MODELO
# ---------------------------------------------------------------------------
N = 4            # expoente: controla o quanto a procura "explode" no fim
TAU = 7          # escala de tempo (dias)
PRAZO = 30       # dia em que as inscrições fecham
PASSO = 0.1      # resolução do gráfico (dias)


def acessos(t: float) -> float:
    """A(t) = t^4 · e^(-t/7): acessos por dia no dia t."""
    return t ** N * math.exp(-t / TAU)


def derivada(t: float) -> float:
    """A'(t) pela regra do produto: t^3 · e^(-t/7) · (4 - t/7)."""
    return t ** (N - 1) * math.exp(-t / TAU) * (N - t / TAU)


def segunda_derivada(t: float) -> float:
    """A''(t) = t^2 · e^(-t/7) · [12 - 8t/7 + t^2/49]."""
    return t ** (N - 2) * math.exp(-t / TAU) * (
        N * (N - 1) - 2 * N * t / TAU + t ** 2 / TAU ** 2
    )


def derivada_numerica(t: float, h: float = 1e-4) -> float:
    """Confere a derivada pelo limite da razão incremental (diferença central)."""
    return (acessos(t + h) - acessos(t - h)) / (2 * h)


def integral_simpson(a: float, b: float, n: int = 2000) -> float:
    """Integral de A(t) entre a e b pela regra de Simpson (n par)."""
    if b <= a:
        return 0.0
    h = (b - a) / n
    soma = acessos(a) + acessos(b)
    for i in range(1, n):
        soma += (4 if i % 2 else 2) * acessos(a + i * h)
    return soma * h / 3


def decisao(t: float) -> dict:
    """Regra de decisão do EdiHub a partir de A'(t) e A''(t)."""
    d1, d2 = derivada(t), segunda_derivada(t)
    if d2 > 0:
        return {"nivel": "verde", "texto": "Procura acelerando: monitoramento padrão"}
    if d1 > 150:
        return {"nivel": "amarelo", "texto": "Escalar servidores e enviar lembretes"}
    return {"nivel": "vermelho", "texto": "Pico de estresse: capacidade máxima"}


# ---------------------------------------------------------------------------
# 2. ANÁLISE DE CÁLCULO (aparece no terminal)
# ---------------------------------------------------------------------------
def analise() -> dict:
    t_pico = N * TAU                          # A'(t)=0  ->  4 - t/7 = 0
    t_inflexao = TAU * (N - math.sqrt(N))     # A''(t)=0 ->  t = 7(4 - 2) = 14
    total_prazo = integral_simpson(0, PRAZO)
    ultima_semana = integral_simpson(PRAZO - 7, PRAZO)
    return {
        "t_pico": t_pico,
        "a_pico": acessos(t_pico),
        "t_inflexao": t_inflexao,
        "d_max": derivada(t_inflexao),
        "total_prazo": total_prazo,
        "ultima_semana": ultima_semana,
        "pct_ultima_semana": 100 * ultima_semana / total_prazo,
        "media_diaria": total_prazo / PRAZO,
        "limite_inf": 0.0,                    # t^4 / e^(t/7) -> 0 (L'Hôpital)
        "total_teorico": math.factorial(N) * TAU ** (N + 1),  # ∫0^∞ = 4!·7^5
    }


def imprimir(r: dict) -> None:
    print("=" * 58)
    print("  EdiHub · Cálculo do pico de acessos  |  A(t) = t^4·e^(-t/7)")
    print("=" * 58)
    print(f"  Ponto crítico   A'(t) = 0  ->  t = {r['t_pico']:.0f} dias")
    print(f"  Pico de acessos A({r['t_pico']:.0f})     = {r['a_pico']:,.0f} acessos/dia")
    print(f"  Inflexão        A''(t)= 0  ->  t = {r['t_inflexao']:.0f} dias")
    print(f"  Maior aceleração A'({r['t_inflexao']:.0f})   = {r['d_max']:,.1f} acessos/dia²")
    print(f"  Total no prazo  ∫0^30 A dt = {r['total_prazo']:,.0f} acessos")
    print(f"  Última semana   ∫23^30 A dt = {r['ultima_semana']:,.0f} "
          f"({r['pct_ultima_semana']:.0f}% do total)")
    print(f"  Média diária    {r['media_diaria']:,.0f}  |  pico = "
          f"{r['a_pico'] / r['media_diaria']:.2f}x a média")
    print(f"  lim t->∞ A(t)   = {r['limite_inf']:.0f}")
    print("-" * 58)
    print("  Conferência da derivada (fórmula x limite numérico):")
    for t in (7, 14, 21, 28):
        print(f"    t={t:>2}:  {derivada(t):>9.3f}  x  {derivada_numerica(t):>9.3f}")
    print("=" * 58)


# ---------------------------------------------------------------------------
# 3. DADOS PARA O GRÁFICO
# ---------------------------------------------------------------------------
def gerar_dados() -> dict:
    ts = [round(i * PASSO, 1) for i in range(int(PRAZO / PASSO) + 1)]
    acumulado, soma = [], 0.0
    for i, t in enumerate(ts):
        if i > 0:  # trapézio a cada passo
            soma += (acessos(ts[i - 1]) + acessos(t)) / 2 * PASSO
        acumulado.append(round(soma, 1))
    return {
        "t": ts,
        "A": [round(acessos(t), 2) for t in ts],
        "dA": [round(derivada(t), 3) for t in ts],
        "acum": acumulado,
        "decisao": [decisao(t) for t in ts],
    }


# ---------------------------------------------------------------------------
# 4. PÁGINA HTML
# ---------------------------------------------------------------------------
HTML = r"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>EdiHub · Cálculo do Pico de Acessos</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<style>
  :root{
    --bg:#f4f6fb; --card:#ffffff; --ink:#14213d; --muted:#5b6478; --line:#e3e7f0;
    --azul:#2f5bea; --roxo:#7b4ce0; --laranja:#f08a24; --vermelho:#e0434b; --verde:#1fa971;
  }
  *{box-sizing:border-box;margin:0;padding:0}
  body{font-family:Inter,system-ui,sans-serif;background:var(--bg);color:var(--ink);padding:28px 16px}
  .wrap{max-width:1040px;margin:0 auto;background:var(--card);border-radius:18px;
        box-shadow:0 10px 40px rgba(20,33,61,.08);padding:32px 28px}
  .tag{display:inline-block;font-size:11px;font-weight:700;letter-spacing:.12em;
       color:var(--azul);background:#e9efff;padding:5px 10px;border-radius:99px}
  h1{font-size:28px;font-weight:800;margin:12px 0 6px;letter-spacing:-.02em}
  .sub{color:var(--muted);font-size:15px}
  .sub b{color:var(--ink)}
  .slider{margin:24px 0 20px;background:#f0f3fa;border-radius:14px;padding:18px 22px}
  .slider label{display:flex;justify-content:space-between;font-weight:600;font-size:14px;margin-bottom:10px}
  .slider label span{color:var(--azul);font-size:18px}
  input[type=range]{width:100%;accent-color:var(--azul);height:6px;cursor:pointer}
  .marcos{display:flex;justify-content:space-between;font-size:11px;color:var(--muted);margin-top:6px}
  .cards{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}
  .card{border:1px solid var(--line);border-radius:14px;padding:16px;border-top:4px solid var(--c)}
  .card h3{font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);font-weight:700}
  .card p{font-size:12.5px;color:var(--muted);margin:4px 0 10px}
  .card .v{font-size:22px;font-weight:800;color:var(--c)}
  .card .v small{font-size:12px;font-weight:600}
  .card.decisao .v{font-size:15px;line-height:1.35}
  .graf{margin-top:22px}
  .rodape{margin-top:18px;padding-top:16px;border-top:1px solid var(--line);
          display:flex;flex-wrap:wrap;gap:8px 22px;font-size:12.5px;color:var(--muted)}
  .rodape b{color:var(--ink)}
  @media(max-width:820px){.cards{grid-template-columns:repeat(2,1fr)}h1{font-size:22px}}
  @media(max-width:460px){.cards{grid-template-columns:1fr}.wrap{padding:22px 16px}}
</style>
</head>
<body>
<div class="wrap">
  <span class="tag">EDIHUB · CITIZENTECH · DIFFERENTIATED PROBLEM SOLVING</span>
  <h1>Cálculo em Ação: o pico de acessos antes do prazo</h1>
  <p class="sub">Modelo: <b>A(t) = t⁴ · e<sup>−t/7</sup></b> &nbsp;·&nbsp; t = dias desde a abertura do edital (inscrições fecham no dia 30)</p>

  <div class="slider">
    <label>Dia selecionado (t) <span id="tval">0,0</span></label>
    <input type="range" id="t" min="0" max="__MAX__" step="1" value="0">
    <div class="marcos"><span>Abertura (0)</span><span>Inflexão (14)</span><span>Pico (28)</span><span>Prazo (30)</span></div>
  </div>

  <div class="cards">
    <div class="card" style="--c:var(--azul)"><h3>Função A(t)</h3><p>Acessos no dia</p><div class="v" id="cA">0</div></div>
    <div class="card" style="--c:var(--vermelho)"><h3>Derivada A'(t)</h3><p>Ritmo de crescimento</p><div class="v" id="cD">0</div></div>
    <div class="card" style="--c:var(--roxo)"><h3>Integral ∫A(t)dt</h3><p>Acessos acumulados</p><div class="v" id="cI">0</div></div>
    <div class="card decisao" id="cardDec" style="--c:var(--verde)"><h3>Decisão do EdiHub</h3><p>Ação na plataforma</p><div class="v" id="cX">—</div></div>
  </div>

  <div class="graf" id="g1" style="height:420px"></div>
  <div class="graf" id="g2" style="height:240px"></div>

  <div class="rodape">
    <span><b>Equipe:</b> Bernardo de Paula Rodrigues (RM 572376) · Arthur Moreira Costa (RM 571532) · Henrique Nunes Mororó (RM 574073)</span>
    <span>Global Solution 2026.2 · FIAP · Engenharia de Software 1º ano</span>
  </div>
</div>

<script>
const D = __DADOS__;
const fmt = (x, c=0) => x.toLocaleString('pt-BR', {minimumFractionDigits:c, maximumFractionDigits:c});
const CORES = {verde:'#1fa971', amarelo:'#f08a24', vermelho:'#e0434b'};
const total = D.acum[D.acum.length-1];
const base = {font:{family:'Inter'}, margin:{l:64,r:20,t:30,b:48}, plot_bgcolor:'#fff',
  paper_bgcolor:'#fff', hovermode:'x unified', legend:{orientation:'h', y:1.14, x:0},
  xaxis:{title:'Dias desde a abertura do edital (t)', range:[0,30], gridcolor:'#eef1f6', dtick:2},
};

function linhaV(x, cor, texto){
  return {shape:{type:'line', x0:x, x1:x, y0:0, y1:1, yref:'paper', line:{color:cor, dash:'dot', width:1.5}},
          ann:{x:x, y:1, yref:'paper', text:texto, showarrow:false, font:{size:11, color:cor}, yanchor:'bottom'}};
}
const marcos = [linhaV(14,'#7b4ce0','inflexão · dia 14'), linhaV(28,'#e0434b','pico · dia 28')];

function desenhar(i){
  const t = D.t[i], a = D.A[i], d = D.dA[i];
  // reta tangente: y = A(t) + A'(t)(x - t), num trecho de ±3 dias
  const x0 = Math.max(0, t-3), x1 = Math.min(30, t+3);
  const tang = {x:[x0,x1], y:[a + d*(x0-t), a + d*(x1-t)], mode:'lines', name:"Reta tangente A'(t)",
                line:{color:'#e0434b', dash:'dash', width:2}, hoverinfo:'skip'};
  const area = {x:D.t.slice(0,i+1), y:D.A.slice(0,i+1), fill:'tozeroy', mode:'none',
                fillcolor:'rgba(123,76,224,.16)', name:'Área = acessos acumulados', hoverinfo:'skip'};
  const curva = {x:D.t, y:D.A, mode:'lines', name:'Acessos A(t)', line:{color:'#2f5bea', width:3},
                 hovertemplate:'%{y:,.0f} acessos<extra></extra>'};
  const ponto = {x:[t], y:[a], mode:'markers', name:'Dia atual', marker:{size:12, color:'#14213d'}, hoverinfo:'skip'};

  Plotly.react('g1', [area, curva, tang, ponto], {...base,
    yaxis:{title:'Acessos / dia', range:[0,12500], gridcolor:'#eef1f6', separatethousands:true},
    shapes:marcos.map(m=>m.shape), annotations:marcos.map(m=>m.ann)}, {displayModeBar:false, responsive:true});

  const deriv = {x:D.t, y:D.dA, mode:'lines', name:"A'(t)", line:{color:'#e0434b', width:2.5},
                 hovertemplate:'%{y:,.1f} acessos/dia²<extra></extra>'};
  const pd = {x:[t], y:[d], mode:'markers', name:'Dia atual', marker:{size:10, color:'#14213d'}, hoverinfo:'skip'};
  Plotly.react('g2', [deriv, pd], {...base, showlegend:false, margin:{l:64,r:20,t:34,b:48},
    title:{text:"Derivada A'(t): velocidade da procura (zera no pico)", font:{size:14}, x:0},
    yaxis:{title:'acessos / dia²', gridcolor:'#eef1f6', zeroline:true, zerolinecolor:'#14213d'},
    shapes:marcos.map(m=>m.shape)}, {displayModeBar:false, responsive:true});

  document.getElementById('tval').textContent = fmt(t,1);
  document.getElementById('cA').innerHTML = fmt(a) + ' <small>acessos</small>';
  document.getElementById('cD').innerHTML = (d>0?'+':'') + fmt(d,1) + ' <small>/dia²</small>';
  document.getElementById('cI').innerHTML = fmt(D.acum[i]) + ' <small>(' + fmt(100*D.acum[i]/total) + '%)</small>';
  const dec = D.decisao[i];
  document.getElementById('cX').textContent = dec.texto;
  document.getElementById('cardDec').style.setProperty('--c', CORES[dec.nivel]);
}

const s = document.getElementById('t');
s.addEventListener('input', e => desenhar(+e.target.value));
desenhar(0);
</script>
</body>
</html>
"""


def gerar_html(dados: dict, arquivo: str = "index.html") -> None:
    pagina = (HTML.replace("__DADOS__", json.dumps(dados, separators=(",", ":")))
                  .replace("__MAX__", str(len(dados["t"]) - 1)))
    with open(arquivo, "w", encoding="utf-8") as f:
        f.write(pagina)
    print(f"  Página gerada: {arquivo}  (abra no navegador ou suba na Vercel)")


if __name__ == "__main__":
    resultado = analise()
    imprimir(resultado)
    gerar_html(gerar_dados())
