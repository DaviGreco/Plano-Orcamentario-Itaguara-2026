import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.offline import plot

# --- 1. DADOS ORIGINAIS ---
entries = [
    ("01.000", "PODER LEGISLATIVO", "3.200.000,00"),
    ("01.001", "CÂMARA MUNICIPAL", "3.200.000,00"),
    ("02.000", "PODER EXECUTIVO", "81.813.385,22"),
    ("02.001", "GABINETE DO PREFEITO", "710.000,00"),
    ("02.002", "PROCURADORIA GERAL", "593.307,69"),
    ("02.012", "FUNDO MUNICIPAL DE SAÚDE", "26.295.700,00"),
    ("02.013", "FUNDO MUN. CRIANÇA E ADOLESCENTE", "30.000,00"),
    ("02.014", "FUNDO MUN. ASSISTÊNCIA SOCIAL", "2.359.608,30"),
    ("02.015", "FUNDO MUNICIPAL DE TURISMO", "204.000,00"),
    ("02.017", "FUNDO MUNICIPAL DE CULTURA", "2.969.500,00"),
    ("02.018", "FUNDO MUNICIPAL DO IDOSO", "35.000,00"),
    ("02.033", "DIVISÃO DE ARRECADAÇÃO", "195.000,00"),
    ("02.035", "DIVISÃO DE APOIO OPERACIONAL", "8.533.770,37"),
    ("02.041", "DIVISÃO DE OBRAS", "10.752.300,30"),
    ("02.042", "DIVISÃO DE LIMPEZA URBANA", "732.000,00"),
    ("02.043", "ILUMINAÇÃO PÚBLICA", "1.100.500,00"),
    ("02.046", "ESTRADAS DE RODAGEM", "1.021.100,00"),
    ("02.048", "DIVISÃO DE AGROPECUÁRIA", "265.100,00"),
    ("02.049", "FUNDO MUN. DE MEIO AMBIENTE", "220.000,00"),
    ("02.051", "ENSINO FUNDAMENTAL (25%)", "14.518.870,38"),
    ("02.053", "ENSINO INFANTIL", "8.110.379,62"),
    ("02.054", "ENSINO FUNDAMENTAL (N/ COMP)", "1.751.148,56"),
    ("02.072", "FUNDO PATRIMONIO CULTURAL", "893.100,00"),
    ("02.091", "DIVISÃO DE ESPORTE", "488.000,00"),
    ("02.092", "DIVISÃO DE LAZER E JUVENTUDE", "35.000,00"),
    ("03.000", "AUTARQUIA - SAAE", "8.486.614,78"),
    ("03.001", "SAAE", "8.486.614,78")
]

# --- 2. PROCESSAMENTO ---
df = pd.DataFrame(entries, columns=["Code", "Name", "ValueStr"])

def converter_e_limpar(valor):
    return float(valor.strip().replace('.', '').replace(',', '.'))

def formatar_brl(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

df['Value'] = df['ValueStr'].apply(converter_e_limpar)
df['Formatted'] = df['Value'].apply(formatar_brl)

# Hierarquia
df['ParentCode'] = df['Code'].apply(lambda x: x[:2] + ".000" if x.endswith("000") else x[:2] + ".000")
df['IsParent'] = df['Code'] == df['ParentCode']
parents = df[df['IsParent']].copy()
children = df[~df['IsParent']].copy()

# Categorização
def categorizar(nome):
    n = nome.upper()
    if 'SAÚDE' in n: return 'Saúde'
    if 'ENSINO' in n or 'EDUCAÇÃO' in n: return 'Educação'
    if any(x in n for x in ['OBRAS', 'INFRAESTRUTURA', 'LIMPEZA', 'ILUMINAÇÃO', 'ESTRADAS']): return 'Infraestrutura e Obras'
    if 'SAAE' in n: return 'Saneamento (SAAE)'
    if 'LEGISLATIVO' in n or 'CÂMARA' in n: return 'Legislativo'
    if any(x in n for x in ['SOCIAL', 'CRIANÇA', 'IDOSO']): return 'Assistência Social'
    if any(x in n for x in ['CULTURA', 'PATRIMONIO', 'TURISMO']): return 'Cultura e Turismo'
    if 'APOIO OPERACIONAL' in n or 'ARRECADAÇÃO' in n or 'GABINETE' in n or 'PROCURADORIA' in n: return 'Administração Geral'
    return 'Outros'

children['Category'] = children['Name'].apply(categorizar)

# --- 3. PREPARAÇÃO DO DETALHAMENTO (CORREÇÃO DE FORMATO) ---
# Criamos uma linha HTML completa para cada sub-item
children['DetailString'] = children.apply(
    lambda x: f"<span style='font-size:12px; color:#ddd;'>• {x['Name']} ({x['Code']}):</span> <b style='color:#fff;'>{x['Formatted']}</b>", axis=1
)

# Agregamos TUDO em uma única string HTML pronta para o gráfico
df_v2 = children.groupby('Category').agg({
    'Value': 'sum',
    'DetailString': lambda x: '<br>'.join(x) 
}).reset_index().sort_values('Value', ascending=False)

df_v2['FormattedTotal'] = df_v2['Value'].apply(formatar_brl)

# Criamos a coluna final 'HoverHTML' que contém TUDO que vai aparecer no hover
# CORREÇÃO AQUI: Usamos caracteres de texto para a linha, em vez de HTML <hr>
df_v2['HoverHTML'] = df_v2.apply(
    lambda row: (
        f"Total da Área: <b>{row['FormattedTotal']}</b><br>"
        f"<br>────────────────────────────────<br>"
        f"<b>DETALHAMENTO:</b><br>"
        f"{row['DetailString']}"
    ), axis=1
)

# --- 4. PREPARAR DEMAIS GRÁFICOS ---
df_v1 = parents.copy()
df_v1['Label'] = df_v1['Name'].replace({
    'PODER LEGISLATIVO': 'Legislativo', 
    'PODER EXECUTIVO': 'Executivo', 
    'AUTARQUIA - SAAE': 'SAAE'
})

df_sorted = children.sort_values('Value', ascending=False)
df_top = df_sorted.head(10).copy()
others_val = df_sorted.iloc[10:]['Value'].sum()
df_others = pd.DataFrame([{
    'Name': 'DEMAIS UNIDADES MENORES', 
    'Value': others_val, 
    'Formatted': formatar_brl(others_val)
}])
df_v3 = pd.concat([df_top, df_others])

# --- 5. GERAÇÃO DOS GRÁFICOS ---
layout_base = dict(
    margin=dict(t=0, b=0, l=0, r=0),
    height=320,
    font=dict(family="Segoe UI, sans-serif", size=13, color="#444"),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    showlegend=True,
    legend=dict(itemclick=False, itemdoubleclick=False, orientation="v", y=0.5, x=1.05, xanchor="left", yanchor="middle")
)

# Gráfico 1
fig1 = go.Figure(data=[go.Pie(
    labels=df_v1['Label'], values=df_v1['Value'].tolist(), customdata=df_v1['Formatted'],
    hole=0.6, marker=dict(colors=['#3498db', '#e74c3c', '#2ecc71'], line=dict(color='#fff', width=3)),
    textinfo='percent', textposition='inside', 
    hovertemplate="<b>%{label}</b><br>Valor: %{customdata}<br>Percentual: %{percent:.1%}<extra></extra>"
)])
fig1.update_layout(**layout_base)
div1 = plot(fig1, output_type='div', include_plotlyjs=False)

# Gráfico 2 - CORRIGIDO (Usa a coluna HoverHTML inteira)
fig2 = go.Figure(data=[go.Pie(
    labels=df_v2['Category'], 
    values=df_v2['Value'].tolist(), 
    customdata=df_v2['HoverHTML'], # Passamos o HTML completo aqui
    hole=0.6, 
    marker=dict(colors=px.colors.qualitative.Pastel, line=dict(color='#fff', width=2)),
    textinfo='percent+label', 
    textposition='outside',
    # Hover template Simplificado (infalível)
    hovertemplate=(
        "<span style='font-size:16px;'><b>%{label}</b></span><br>" +
        "%{customdata}" + # Apenas imprime o HTML que preparamos no Python
        "<extra></extra>"
    )
)])
fig2.update_layout(**layout_base)
div2 = plot(fig2, output_type='div', include_plotlyjs=False)

# Gráfico 3
fig3 = go.Figure(data=[go.Pie(
    labels=df_v3['Name'], values=df_v3['Value'].tolist(), customdata=df_v3['Formatted'],
    hole=0.6, marker=dict(colors=px.colors.qualitative.Set2, line=dict(color='#fff', width=2)),
    textinfo='percent', textposition='inside', 
    hovertemplate="<b>%{label}</b><br>Valor: %{customdata}<br>Percentual: %{percent:.1%}<extra></extra>"
)])
fig3.update_layout(**layout_base)
div3 = plot(fig3, output_type='div', include_plotlyjs=False)

# --- 6. HTML FINAL ---
html_template = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Painel Orçamentário Itaguara 2026</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap" rel="stylesheet">
    <style>
        :root {{ --primary: #2c3e50; --accent: #3498db; --bg-body: #f4f7f6; --bg-card: #ffffff; --text: #333; }}
        body {{ font-family: 'Roboto', 'Segoe UI', sans-serif; background-color: var(--bg-body); color: var(--text); margin: 0; padding: 0; }}
        
        .header {{
            background: linear-gradient(135deg, #2c3e50, #4ca1af);
            color: white; padding: 60px 20px 100px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        .header h1 {{ margin: 0; font-size: 2.5rem; font-weight: 700; }}
        .header p {{ margin: 10px 0 0; font-size: 1.1rem; opacity: 0.9; }}
        .badge {{ display: inline-block; background: rgba(255,255,255,0.25); padding: 8px 16px; border-radius: 50px; margin-top: 15px; font-weight: bold; }}

        .container {{ max-width: 1000px; margin: -60px auto 40px; padding: 0 20px; display: grid; gap: 40px; }}
        
        .card {{ background: var(--bg-card); border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); padding: 30px; border: 1px solid #eef0f2; }}
        .card-header {{ border-bottom: 2px solid #f0f0f0; padding-bottom: 15px; margin-bottom: 20px; display: flex; align-items: center; justify-content: space-between; }}
        .card-title h2 {{ margin: 0; font-size: 1.4rem; color: var(--primary); }}
        .card-title span {{ font-size: 0.9rem; color: #888; display: block; }}
        .chart-wrapper {{ width: 100%; min-height: 320px; }}

        /* Força alinhamento à esquerda no tooltip para leitura fácil */
        .hovertext {{ text-align: left !important; }}

        .btn-download {{
            display: inline-block;
            background-color: var(--accent);
            color: white;
            padding: 12px 24px;
            text-decoration: none;
            border-radius: 50px;
            font-weight: bold;
            margin-bottom: 15px;
            box-shadow: 0 4px 10px rgba(52, 152, 219, 0.3);
            transition: all 0.3s ease;
        }}
        .btn-download:hover {{
            background-color: #2980b9;
            transform: translateY(-2px);
            box-shadow: 0 6px 15px rgba(52, 152, 219, 0.4);
        }}

        .footer {{ text-align: center; padding: 40px; color: #aaa; font-size: 0.9rem; border-top: 1px solid #ddd; margin-top: 20px; }}
        
        @media (max-width: 768px) {{ .header h1 {{ font-size: 1.8rem; }} .container {{ margin-top: -40px; gap: 20px; }} }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Painel Orçamentário 2026</h1>
        <p>Município de Itaguara - MG</p>
        <div class="badge">Total: R$ 93.500.000,00</div>
    </div>
    <div class="container">
        <div class="card">
            <div class="card-header"><div class="card-title"><span>Visão Geral</span><h2>1. Distribuição por Poder</h2></div></div>
            <div class="chart-wrapper">{div1}</div>
        </div>
        <div class="card">
            <div class="card-header"><div class="card-title"><span>Áreas Funcionais</span><h2>2. Onde o dinheiro será investido?</h2></div></div>
            <div class="chart-wrapper">{div2}</div>
        </div>
        <div class="card">
            <div class="card-header"><div class="card-title"><span>Detalhamento</span><h2>3. As 10 Maiores Unidades (Secretarias/Fundos)</h2></div></div>
            <div class="chart-wrapper">{div3}</div>
        </div>
    </div>
    <div class="footer">
        <a href="Planejamento das despesas.pdf" download class="btn-download">📄 Baixar Documento Oficial (PDF)</a>
        <br>
        Gerado automaticamente a partir dos dados oficiais do Planejamento 2026.
    </div>
</body>
</html>
"""

# Salvar Arquivo
filename = "painel_orcamento_final.html"
with open(filename, "w", encoding="utf-8") as f:
    f.write(html_template)

print(f"Arquivo gerado: {filename}")