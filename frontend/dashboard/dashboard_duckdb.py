import duckdb
import os
from dotenv import load_dotenv
import plotly.graph_objects as go
from taipy.gui import Markdown

# Carrega as variáveis de ambiente para o RDS PostgreSQL
load_dotenv()

# Variáveis globais
selected_date = None
total_cadastros = 0
total_pedidos = 0
ticket_medio = 0

fig_cadastros = go.Figure()
fig_pedidos = go.Figure()
fig_receita_ticket = go.Figure()

# Função para conectar ao banco de dados PostgreSQL via DuckDB
def connect_duckdb():
    POSTGRES_HOSTNAME = os.getenv('POSTGRES_HOSTNAME')
    POSTGRES_DBNAME = os.getenv('POSTGRES_DBNAME')
    POSTGRES_USER = os.getenv('POSTGRES_USER')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
    POSTGRES_PORT = os.getenv('POSTGRES_PORT')

    con = duckdb.connect()
    con.execute("""
        INSTALL postgres_scanner;
        LOAD postgres_scanner;
    """)
    con.execute(f"""
        ATTACH 'dbname={POSTGRES_DBNAME} user={POSTGRES_USER} host={POSTGRES_HOSTNAME} port={POSTGRES_PORT} password={POSTGRES_PASSWORD}' 
        AS postgres_db (TYPE POSTGRES, SCHEMA 'public');
    """)
    return con

# Função para carregar os KPIs de pedidos e cadastros
def load_kpis(con, selected_date=None):
    # Se uma data foi passada, filtramos diretamente no DuckDB para evitar sobrecarregar a memória
    date_filter = ""
    if selected_date is not None:
        date_filter = f" WHERE data_pedido >= '{selected_date}'"

    query = f"""
        SELECT data_pedido, estado, total_pedidos_faturados, receita_total, ticket_medio
        FROM postgres_db.gold_kpi_faturados_por_dia_estado_regiao
        {date_filter}
    """
    # Em vez de carregar em pandas, usamos DuckDB para manipulação de dados
    return con.execute(query)

# Função para atualizar os gráficos e KPIs
def update_dashboard(state):
    global total_cadastros, total_pedidos, ticket_medio, fig_cadastros, fig_pedidos, fig_receita_ticket

    conn = connect_duckdb()
    df_filtered = load_kpis(conn, state.selected_date)

    # Atualizar KPIs
    total_cadastros = df_filtered.count('data_pedido').fetchone()[0]  # Contar o número total de cadastros
    total_pedidos = df_filtered.sum('total_pedidos_faturados').fetchone()[0]  # Somar o total de pedidos faturados
    ticket_medio = df_filtered.avg('ticket_medio').fetchone()[0]  # Média do ticket médio

    # Criar gráficos diretamente com DuckDB sem pandas
    # Gráfico de cadastros
    df_cadastros = df_filtered.execute("""
        SELECT strftime(data_pedido, '%Y-%m') as mes, COUNT(*) as cadastros
        FROM postgres_db.gold_kpi_faturados_por_dia_estado_regiao
        GROUP BY mes
        ORDER BY mes
    """).fetchall()

    fig_cadastros = go.Figure()
    fig_cadastros.add_trace(go.Bar(x=[row[0] for row in df_cadastros], y=[row[1] for row in df_cadastros], name="Cadastros"))
    state.fig_cadastros = fig_cadastros

    # Gráfico de pedidos
    df_pedidos = df_filtered.execute("""
        SELECT strftime(data_pedido, '%Y-%m') as mes, SUM(total_pedidos_faturados) as pedidos
        FROM postgres_db.gold_kpi_faturados_por_dia_estado_regiao
        GROUP BY mes
        ORDER BY mes
    """).fetchall()

    fig_pedidos = go.Figure()
    fig_pedidos.add_trace(go.Bar(x=[row[0] for row in df_pedidos], y=[row[1] for row in df_pedidos], name="Pedidos"))
    state.fig_pedidos = fig_pedidos

    # Gráfico de receita e ticket médio
    df_receita = df_filtered.execute("""
        SELECT strftime(data_pedido, '%Y-%m') as mes, SUM(receita_total) as receita, AVG(ticket_medio) as ticket_medio
        FROM postgres_db.gold_kpi_faturados_por_dia_estado_regiao
        GROUP BY mes
        ORDER BY mes
    """).fetchall()

    fig_receita_ticket = go.Figure()
    fig_receita_ticket.add_trace(go.Bar(x=[row[0] for row in df_receita], y=[row[1] for row in df_receita], name="Receita", yaxis='y1'))
    fig_receita_ticket.add_trace(go.Scatter(x=[row[0] for row in df_receita], y=[row[2] for row in df_receita], mode='lines+markers', name="Ticket Médio", yaxis='y2'))

    # Configuração dos eixos independentes para o gráfico de receita e ticket médio
    fig_receita_ticket.update_layout(
        title="Receita e Ticket Médio ao Longo dos Meses",
        xaxis_title="Mês",
        yaxis_title="Receita",
        yaxis2=dict(
            title="Ticket Médio",
            overlaying='y',  # Sobrepõe o eixo y principal
            side='right',    # Eixo à direita
            showgrid=False   # Remove a grid do segundo eixo
        )
    )
    state.fig_receita_ticket = fig_receita_ticket

    conn.close()

# Função para carregar markdown
def load_markdown_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

# Carregar e processar os dados no início
dashboard_md_content = load_markdown_file("frontend/dashboard/dashboard_duckdb.md")
dashboard_duckdb_md = Markdown(dashboard_md_content)
