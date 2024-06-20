from nomad.config.models.plugins import ParserEntryPoint


class HySprintParserEntryPoint(ParserEntryPoint):

    def load(self):
        from nomad_hysprint.parsers.hysprint_parser import HySprintParser
        return HySprintParser(**self.dict())


hysprint_parser = HySprintParserEntryPoint(
    name='HySprintParser',
    description='Parser for Hysprint files',
    mainfile_name_re='^(.+\.?.+\.((eqe|jv|jvi|pl|pli|hy|spv|env|uvvis|PL|JV|PLI|EQE|SEM|sem|xrd)\..{1,4})|.+\.nk)$',
    mainfile_mime_re='(application|text|image)/.*'
)
