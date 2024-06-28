from argparse import Action
from pytoolbelt.core.data_classes.component_metadata import ComponentMetadata


class ParseNameVersion(Action):

    def __call__(self, parser, namespace, values, option_string=None):
        name_versions = []
        for value in values:
            name_versions.append(ComponentMetadata.from_string(value))
        setattr(namespace, self.dest, name_versions)


class ParsePtVenvMeta(Action):

    def __call__(self, parser, namespace, values, option_string=None):
        meta = (ComponentMetadata.as_ptvenv(values))
        setattr(namespace, self.dest, meta)
