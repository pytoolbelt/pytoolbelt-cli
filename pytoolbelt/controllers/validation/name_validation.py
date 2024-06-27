from argparse import Action
from pytoolbelt.core.data_classes.name_version import NameVersion


class ParseNameVersion(Action):

    def __call__(self, parser, namespace, values, option_string=None):
        name_versions = []
        for value in values:
            name_versions.append(NameVersion.from_string(value))
        setattr(namespace, self.dest, name_versions)
