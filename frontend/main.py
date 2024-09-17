from taipy.gui import Gui
import taipy.gui.builder as tgb
from dashboard.dashboard import dashboard_md
from dashboard.dashboard_polars import dashboard_md_polars

# Add a navbar to switch from one page to the other
with tgb.Page() as root_page:
    tgb.navbar()
    tgb.text("# Dashboard de KPIs", mode="md")

pages = {
    '/': dashboard_md, 
    "Polars": dashboard_md_polars, 
}

if __name__ == '__main__':
    # Iniciar o GUI do Taipy e rodar o projeto
    gui_multi_pages = Gui(pages=pages)

    # Rodar o core do Taipy
    gui_multi_pages.run(title="Dashboard de KPIs", use_reloader=True)
