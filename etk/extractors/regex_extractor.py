from typing import List
from enum import Enum, auto
from etk.extractor import Extractor, InputType
from etk.etk_extraction import Extraction
import re


class MatchMode(Enum):
    MATCH = auto(),
    SEARCH = auto()


class RegexExtractor(Extractor):
    """
    Extract using Python regular expressions.
    """
    def __init__(self,
                 pattern: str,
                 extractor_name: str,
                 flags=0,
                 ) -> None:
        Extractor.__init__(self,
                           input_type=InputType.TEXT,
                           category="regex",
                           name=extractor_name)
        self._compiled_regex = re.compile(pattern, flags)

    def extract(self, text: str, flags=0, mode: MatchMode=MatchMode.SEARCH) -> List[Extraction]:
        """
        Extracts information from a text using the given regex.
        If the pattern has no groups, it returns a list with a single Extraction.
        If the pattern has groups, it returns a list of Extraction, one for each group.
        Each extraction records the start and end char positions of matches.

        Args:
            text (str): the text to extract from.
            flags (): flags given to search or match.
            mode (): whether to use re.search() or re.match().

        Returns: the List(Extraction) or the empty list if there are no matches.
        """
        pass
