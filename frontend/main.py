from taipy.gui import Gui
from dashboard.dashboard import dashboard_md
from dashboard.dashboard_duckdb import dashboard_duckdb_md

pages = {
    '/': dashboard_md, 
    "Duckdb": dashboard_duckdb_md, 
}

if __name__ == '__main__':
    # Iniciar o GUI do Taipy e rodar o projeto
    gui_multi_pages = Gui(pages=pages)

    # Rodar o core do Taipy
    gui_multi_pages.run(title="Dashboard de KPIs", use_reloader=True)
