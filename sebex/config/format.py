import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import TextIO

import yaml

from sebex.context import Context


class Format(ABC):
    @abstractmethod
    def ext(self) -> str:
        ...

    @abstractmethod
    def load(self, fp: TextIO):
        ...

    @abstractmethod
    def dump(self, data, fp: TextIO):
        ...

    def full_path(self, name: str) -> Path:
        full_path = Context.current().meta_path / name
        full_path = full_path.with_suffix(self.ext())
        return full_path


class JsonFormat(Format):
    def ext(self) -> str:
        return '.json'

    def load(self, fp: TextIO):
        return json.load(fp)

    def dump(self, data, fp: TextIO):
        json.dump(data, fp, indent=2)


@dataclass
class YamlFormat(Format):
    autogenerated: bool = False

    def ext(self) -> str:
        return '.yaml'

    def load(self, fp: TextIO):
        return yaml.safe_load(fp)

    def dump(self, data, fp: TextIO):
        if self.autogenerated:
            fp.write('# File generated automatically. DO NOT EDIT.\n\n')

        yaml.dump(data, fp, default_flow_style=False, sort_keys=False)


class LinesFormat(Format):
    COMMENT = '#'

    def ext(self) -> str:
        return '.txt'

    def load(self, fp: TextIO):
        any_lines = (any_line.strip() for any_line in fp)
        return [line for line in any_lines if line and not line.startswith(self.COMMENT)]

    def dump(self, data, fp: TextIO):
        if not isinstance(data, list):
            raise Exception('LinesFormat support only lists of strings as data type')

        fp.writelines(f'{str(entry).strip()}\n' for entry in data)
