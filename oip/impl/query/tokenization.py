from typing import List

from oip.base.query.query import Query
from oip.base.query.token import QueryToken
from oip.base.query.tokenization import QueryTokenizer


class SimpleQueryTokenizer(QueryTokenizer):
    def tokenize_query(self, query: Query) -> List[QueryToken]:
        tokens = list[QueryToken]()
        query = query.query
        pos = 0
        while pos < len(query):
            char = query[pos]

            if char.isspace():
                pos += 1
                continue

            if char == "(":
                tokens.append(QueryToken("LPAR", "("))
                pos += 1
                continue

            if char == ")":
                tokens.append(QueryToken("RPAR", ")"))
                pos += 1
                continue

            if char.isalpha():
                start = pos
                while pos < len(query) and query[pos].isalpha():
                    pos += 1

                word = query[start:pos]

                if word.upper() in ("AND", "OR", "NOT"):
                    tokens.append(QueryToken(word.upper(), word))
                else:
                    tokens.append(QueryToken("WORD", word))

                continue
            else:
                print(f"Invalid character '{char}' at position {pos}")
                return list[QueryToken]()

        tokens.append(QueryToken("EOF", "EOF"))

        return tokens


DEFAULT_QUERY_TOKENIZER = SimpleQueryTokenizer()


def default_query_tokenizer() -> QueryTokenizer:
    return DEFAULT_QUERY_TOKENIZER
