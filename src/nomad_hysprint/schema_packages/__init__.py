from nomad.config.models.plugins import SchemaPackageEntryPoint


class HySprintPackageEntryPoint(SchemaPackageEntryPoint):
    def load(self):
        from nomad_hysprint.schema_packages.hysprint_package import m_package

        return m_package


class SOLAIPackageEntryPoint(SchemaPackageEntryPoint):
    def load(self):
        from nomad_hysprint.schema_packages.solai_package import m_package

        return m_package


class SolarTabPackageEntryPoint(SchemaPackageEntryPoint):
    def load(self):
        from nomad_hysprint.schema_packages.solartab_package import m_package

        return m_package


class InkRecyclingPackageEntryPoint(SchemaPackageEntryPoint):
    def load(self):
        from nomad_hysprint.schema_packages.ink_recycling_package import m_package

        return m_package


hysprint_package = HySprintPackageEntryPoint(
    name='HySprint',
    description='Package for HZB HySprint Lab',
)

solai_package = SOLAIPackageEntryPoint(
    name='SolAI',
    description='Package for SOLAI specific schema',
)

solartab_package = SolarTabPackageEntryPoint(
    name='SolarTab',
    description='Package for SolarTab specific schema',
)

ink_recycling_package = InkRecyclingPackageEntryPoint(
    name='InkRecycling',
    description='Package for ink recycling specific schema',
)
