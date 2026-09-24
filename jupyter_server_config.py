"""Inicia el dashboard bajo el proxy de Jupyter cuando Binder abre /viajeros/."""
import sys

c = get_config()  # Objeto de configuración que entrega Jupyter.
c.ServerProxy.servers = {
    "viajeros": {
        "command": [sys.executable, "dashboard_viajeros.py"],
        "environment": {
            "PORT": "{port}",
            "DASH_REQUESTS_PATHNAME_PREFIX": "{base_url}viajeros/",
        },
        "absolute_url": False,
        "timeout": 60,
        "launcher_entry": {"title": "Viajeros LATAM 2022"},
    }
}
