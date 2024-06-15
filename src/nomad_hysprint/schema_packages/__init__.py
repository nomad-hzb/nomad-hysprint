from nomad.config.models.plugins import SchemaPackageEntryPoint


class HySprintPackageEntryPoint(SchemaPackageEntryPoint):

    def load(self):
        from nomad_hysprint.schema_packages.hysprint_package import m_package
        return m_package


hysprint_package = HySprintPackageEntryPoint(
    name='HySprint',
    description='Package for HZB HySprint Lab',
)
