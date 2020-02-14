from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sebex.config import ProjectHandle
    from sebex.analysis.analyzer import Analyzer


class Language(Enum):
    ELIXIR = 'elixir'
    UNKNOWN = 'unknown'

    @classmethod
    def detect(cls, project: 'ProjectHandle') -> 'Language':
        from . import elixir

        if elixir.mix_file(project).exists():
            return cls.ELIXIR

        return cls.UNKNOWN

    @property
    def analyzer(self) -> 'Analyzer':
        from . import elixir

        if self == self.ELIXIR:
            return elixir.analyze

        raise KeyError(f'There is no analyzer for language: {self.value}')