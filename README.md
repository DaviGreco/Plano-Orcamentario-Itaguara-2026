# 📊 Painel Orçamentário Interativo - Itaguara 2026

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-150458)
![Plotly](https://img.shields.io/badge/Plotly-Interactive%20Graphs-3F4F75)
![Status](https://img.shields.io/badge/Status-Concluído-success)

> Um dashboard interativo gerado via Python para visualização clara e transparente das despesas municipais planejadas para o ano de 2026.

## 🎯 Sobre o Projeto

Este projeto tem como objetivo transformar dados orçamentários brutos (normalmente encontrados em PDFs técnicos e extensos) em uma interface visual, interativa e acessível para qualquer cidadão.

Utilizando a biblioteca **Plotly**, o script gera um arquivo HTML autônomo (sem necessidade de servidor backend) contendo gráficos que detalham a distribuição de verbas do município de **Itaguara-MG**.

### ✨ Funcionalidades

* **Processamento de Dados:** Limpeza e estruturação hierárquica dos dados orçamentários (Órgão > Unidade).
* **Visualização Interativa:** Gráficos de rosca (Donut Charts) com detalhamento ao passar o mouse (Hover).
* **Categorização Inteligente:** Agrupamento automático das unidades por áreas funcionais (Saúde, Educação, Infraestrutura, etc.).
* **Detalhamento Drill-down:** Ao passar o mouse sobre uma área (ex: "Administração Geral"), o painel lista todas as sub-unidades que compõem aquele valor.
* **Exportação HTML:** O resultado é um arquivo `.html` único, responsivo e estilizado com CSS moderno.
* **Acesso ao Documento Oficial:** Botão integrado para download do PDF original da LOA (Lei Orçamentária Anual).

## 🛠️ Tecnologias Utilizadas

* **Python:** Linguagem base para o script.
* **Pandas:** Manipulação e estruturação dos dados (DataFrames).
* **Plotly Graph Objects & Express:** Criação dos gráficos vetoriais interativos.
* **HTML/CSS:** Injeção de estilos personalizados para o layout do dashboard.

## 🚀 Como Executar o Projeto

### Pré-requisitos

Certifique-se de ter o Python instalado. Em seguida, instale as bibliotecas necessárias:

```bash
pip install pandas plotly
