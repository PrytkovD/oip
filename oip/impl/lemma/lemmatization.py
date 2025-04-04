from typing import Set

import nltk
from nltk import WordNetLemmatizer, pos_tag
from nltk.corpus import wordnet

from oip.base.lemma.lemma import PageLemmas, Lemma
from oip.base.lemma.lemmatization import Lemmatizer, TokenLemmatizer
from oip.base.token.token import PageTokens, Token


class SimpleLemmatizer(Lemmatizer):
    def __init__(self, token_lemmatizer: TokenLemmatizer):
        self._token_lemmatizer = token_lemmatizer

    def lemmatize(self, page_tokens: PageTokens) -> PageLemmas:
        lemmatized_tokens = dict[Token, Set[Token]]()

        for token in page_tokens.tokens:
            lemma = self._token_lemmatizer.lemmatize_token(token)

            if lemmatized_tokens.get(lemma) is None:
                lemmatized_tokens[lemma] = set[Token]()
            lemmatized_tokens[lemma].add(token)

        lemmas = list[Lemma]()
        for lemma, tokens in lemmatized_tokens.items():
            lemmas.append(Lemma(lemma, list(tokens)))

        lemmas = sorted(list(set(lemmas)))

        return PageLemmas(page_tokens.page_url, lemmas)


class NltkTokenLemmatizer(TokenLemmatizer):
    def __init__(self):
        nltk.download('averaged_perceptron_tagger_eng')
        nltk.download('wordnet')
        nltk.download('omw-1.4')
        self._wordnet_lemmatizer = WordNetLemmatizer()

    def lemmatize_token(self, token: Token) -> Token:
        token, tag = pos_tag([token.value])[0]
        wordnet_pos = self._get_wordnet_pos(tag)
        lemma = self._wordnet_lemmatizer.lemmatize(token, wordnet_pos)
        return Token(lemma)

    def _get_wordnet_pos(self, treebank_tag):
        if treebank_tag.startswith('J'):
            return wordnet.ADJ
        elif treebank_tag.startswith('V'):
            return wordnet.VERB
        elif treebank_tag.startswith('N'):
            return wordnet.NOUN
        elif treebank_tag.startswith('R'):
            return wordnet.ADV
        else:
            return wordnet.NOUN


DEFAULT_TOKEN_LEMMATIZER = NltkTokenLemmatizer()


def default_token_lemmatizer() -> TokenLemmatizer:
    return DEFAULT_TOKEN_LEMMATIZER


DEFAULT_LEMMATIZER = SimpleLemmatizer(default_token_lemmatizer())


def default_lemmatizer() -> Lemmatizer:
    return DEFAULT_LEMMATIZER
