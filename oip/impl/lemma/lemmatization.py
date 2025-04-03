from typing import Set

import nltk
from nltk import WordNetLemmatizer, pos_tag
from nltk.corpus import wordnet

from oip.base.lemma.lemma import PageLemmas, Lemma
from oip.base.lemma.lemmatization import Lemmatizer
from oip.base.token.token import PageTokens, Token


class SimpleLemmatizer(Lemmatizer):
    def __init__(self):
        nltk.download('averaged_perceptron_tagger_eng')
        nltk.download('wordnet')
        nltk.download('omw-1.4')

    def lemmatize(self, page_tokens: PageTokens) -> PageLemmas:
        wordnet_lemmatizer = WordNetLemmatizer()
        tagged_tokens = pos_tag([token.value for token in page_tokens.tokens])

        lemmatized_tokens = dict[str, Set[str]]()
        for token, tag in tagged_tokens:
            wordnet_pos = self._get_wordnet_pos(tag)
            lemma = wordnet_lemmatizer.lemmatize(token, wordnet_pos)

            if lemmatized_tokens.get(lemma) is not None:
                lemmatized_tokens[lemma].add(token)
            else:
                lemmatized_tokens[lemma] = {token}

        lemmas = list[Lemma]()
        for lemma, tokens in lemmatized_tokens.items():
            lemmas.append(Lemma(Token(lemma), [Token(token) for token in tokens]))

        return PageLemmas(page_tokens.page_url, lemmas)

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


DEFAULT_LEMMATIZER = SimpleLemmatizer()


def default_lemmatizer() -> Lemmatizer:
    return DEFAULT_LEMMATIZER
