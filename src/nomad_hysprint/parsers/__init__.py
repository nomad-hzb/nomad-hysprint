from nomad.config.models.plugins import ParserEntryPoint


class HySprintParserEntryPoint(ParserEntryPoint):
    def load(self):
        from nomad_hysprint.parsers.hysprint_measurement_parser import HySprintParser

        return HySprintParser(**self.model_dump())


class HySprintExperimentParserEntryPoint(ParserEntryPoint):
    def load(self):
        from nomad_hysprint.parsers.hysprint_batch_parser import (
            HySprintExperimentParser,
        )

        return HySprintExperimentParser(**self.model_dump())


class SolarTabSimulationParserEntryPoint(ParserEntryPoint):
    def load(self):
        from nomad_hysprint.parsers.solartab_simulation_parser import (
            SolarTabSimulationParser,
        )

        return SolarTabSimulationParser(**self.model_dump())


hysprint_parser = HySprintParserEntryPoint(
    name='HySprintParser',
    description='Parser for Hysprint files',
    mainfile_name_re='^(.+\.?.+\.((eqe|jv|jvi|pl|pli|hy|spv|env|uvvis|PL|JV|PLI|EQE|SEM|sem|xrd|mppt)\..{1,4})|.+\.nk)$',
    mainfile_mime_re='(application|text|image)/.*',
)


hysprint_experiment_parser = HySprintExperimentParserEntryPoint(
    name='HySprintBatchParser',
    description='Parser for Hysprint Batch xlsx files',
    mainfile_name_re='^(.+\.xlsx)$',
    # mainfile_contents_re='Experiment Info',
    mainfile_mime_re='(application|text|image)/.*',
)


solartab_sim_parser = SolarTabSimulationParserEntryPoint(
    name='SolarTabSimulationParser',
    description='Parser for Solartab simulation files',
    mainfile_name_re='^.*solartab.*$',
)
