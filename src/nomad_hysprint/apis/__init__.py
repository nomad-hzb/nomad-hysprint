from nomad.config.models.plugins import APIEntryPoint


class PanelDashboardAPIEntryPoint(APIEntryPoint):
    def load(self):
        from nomad_hysprint.apis.panel_dashboard import app

        return app


panel_dashboard_api_entry_point = PanelDashboardAPIEntryPoint(
    prefix='panel_dashboard/',
    name='Panel Dashboard',
    description='API for managing the panel dashboard.',
)
