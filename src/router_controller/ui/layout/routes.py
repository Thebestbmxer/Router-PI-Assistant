from flask import current_app, render_template


def register_layout_routes(app):

    @app.get("/gui-config")
    def gui_config():
        manager = manager.active()

        return render_template(
            "layouts/{layout.id}/gui_config.html",
            layouts=manager.available(),
            active_layout=layout,
        )