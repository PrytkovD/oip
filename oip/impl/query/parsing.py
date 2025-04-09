from abc import abstractmethod
from typing import List, Optional

from oip.base.query.parsing import QueryParser
from oip.base.query.node import QueryNode, WordQueryNode, AndQueryNode, OrQueryNode, NotQueryNode
from oip.base.query.token import QueryToken


class SimpleQueryParser(QueryParser):
    def __init__(self):
        self.tokens = None
        self.pos = 0

    def parse_query_tokens(self, query_tokens: List[QueryToken]) -> QueryNode:
        self.tokens = query_tokens
        self.pos = 0

        try:
            return self.parse()
        except SyntaxError as e:
            print(e.msg)

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else QueryToken("EOF", "EOF")

    def consume(self, expected_type: Optional[str] = None):
        if self.pos >= len(self.tokens):
            raise SyntaxError(f"Unexpected token '{self.peek().value}' at position {self.pos}")
        current_token = self.tokens[self.pos]
        if expected_type is not None and current_token.type != expected_type:
            raise SyntaxError(f"Unexpected token '{self.peek().value}' at position {self.pos}")
        self.pos += 1
        return current_token

    def parse(self):
        node = self.parse_or()
        if self.peek().type != "EOF":
            raise SyntaxError(f"Unexpected token '{self.peek().value}' at position {self.pos}")
        return node

    def parse_or(self):
        node = self.parse_and()
        while self.peek().type == "OR":
            self.consume("OR")
            rhs = self.parse_and()
            node = OrQueryNode(node, rhs)
        return node

    def parse_and(self):
        node = self.parse_not()
        while self.peek().type == "AND":
            self.consume("AND")
            rhs = self.parse_not()
            node = AndQueryNode(node, rhs)
        return node

    def parse_not(self):
        if self.peek().type == "NOT":
            self.consume("NOT")
            child = self.parse_not()
            return NotQueryNode(child)
        else:
            return self.parse_primary()

    def parse_primary(self):
        token = self.peek()
        token_type, token_value = token.type, token.value
        if token_type == "LPAR":
            self.consume("LPAR")
            node = self.parse_or()
            self.consume("RPAR")
            return node
        elif token_type == "WORD":
            self.consume("WORD")
            return WordQueryNode(token_value)
        else:
            raise SyntaxError(f"Unexpected token '{self.peek().value}' at position {self.pos}")


DEFAULT_QUERY_PARSER = SimpleQueryParser()


def default_query_parser() -> QueryParser:
    return DEFAULT_QUERY_PARSER