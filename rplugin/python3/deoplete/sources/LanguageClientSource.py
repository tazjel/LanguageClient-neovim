from functools import partial
from .base import Base
from os import path
import sys
LanguageClientPath = path.dirname(path.dirname(path.dirname(
    path.realpath(__file__))))
# TODO: use relative path.
sys.path.append(LanguageClientPath)
from LanguageClient import LanguageClient  # noqa: E402


class Source(Base):
    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'LanguageClient'
        self.mark = '[LC]'
        self.rank = 1000
        self.min_pattern_length = 1
        self.filetypes = LanguageClient._instance.serverCommands.keys()

        self.__results = {}

    def receiveCompletionResult(self, items, contextid):
        self.__results[contextid] = items

    def convertToDeopleteCandidate(self, item):
        cand = {"word": item["label"]}
        if "kind" in item:
            cand["kind"] = item["kind"]
        if "detail" in item:
            cand["info"] = item["detail"]
        return cand

    def gather_candidates(self, context):
        contextid = id(context)
        if contextid in self.__results:
            items = self.__results[contextid]
            if items is None:  # no response yet
                return ["..."]
            else:  # got result
                context["is_async"] = False
                del self.__results[contextid]
                return [self.convertToDeopleteCandidate(item)
                        for item in items]
        else:  # send request
            context["is_async"] = True
            self.__results[contextid] = None

            args = {}
            args["line"] = context["position"][1] - 1
            args["character"] = context["position"][2] - 1
            args["cb"] = partial(
                    self.receiveCompletionResult, contextid=contextid)
            LanguageClient._instance.textDocument_completion([args])

            return ["..."]  # workarond for deoplete, canot be empty
