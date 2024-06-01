# sentiment_analysis.py
import math
import re
import string
from itertools import product
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

class VaderConstants:
    B_INCR = 0.293
    B_DECR = -0.293
    C_INCR = 0.733
    N_SCALAR = -0.74
    NEGATE = {
        "aint", "arent", "cannot", "cant", "couldnt", "darent", "didnt", "doesnt", "aint't", "aren't", "can't",
        "couldn't", "daren't", "didn't", "doesn't", "dont", "hadnt", "hasnt", "havent", "isnt", "mightnt", "mustnt",
        "neither", "don't", "hadn't", "hasn't", "haven't", "isn't", "mightn't", "mustn't", "neednt", "needn't",
        "never", "none", "nope", "nor", "not", "nothing", "nowhere", "oughtnt", "shant", "shouldnt", "uhuh", "wasnt",
        "werent", "oughtn't", "shan't", "shouldn't", "uh-uh", "wasn't", "weren't", "without", "wont", "wouldnt",
        "won't", "wouldn't", "rarely", "seldom", "despite"
    }
    BOOSTER_DICT = {
        "absolutely": B_INCR, "amazingly": B_INCR, "awfully": B_INCR, "completely": B_INCR, "considerably": B_INCR,
        "decidedly": B_INCR, "deeply": B_INCR, "effing": B_INCR, "enormously": B_INCR, "entirely": B_INCR,
        "especially": B_INCR, "exceptionally": B_INCR, "extremely": B_INCR, "fabulously": B_INCR, "flipping": B_INCR,
        "flippin": B_INCR, "fricking": B_INCR, "frickin": B_INCR, "frigging": B_INCR, "friggin": B_INCR, "fully": B_INCR,
        "fucking": B_INCR, "greatly": B_INCR, "hella": B_INCR, "highly": B_INCR, "hugely": B_INCR, "incredibly": B_INCR,
        "intensely": B_INCR, "majorly": B_INCR, "more": B_INCR, "most": B_INCR, "particularly": B_INCR, "purely": B_INCR,
        "quite": B_INCR, "really": B_INCR, "remarkably": B_INCR, "so": B_INCR, "substantially": B_INCR, "thoroughly": B_INCR,
        "totally": B_INCR, "tremendously": B_INCR, "uber": B_INCR, "unbelievably": B_INCR, "unusually": B_INCR, "utterly": B_INCR,
        "very": B_INCR, "almost": B_DECR, "barely": B_DECR, "hardly": B_DECR, "just enough": B_DECR, "kind of": B_DECR,
        "kinda": B_DECR, "kindof": B_DECR, "kind-of": B_DECR, "less": B_DECR, "little": B_DECR, "marginally": B_DECR,
        "occasionally": B_DECR, "partly": B_DECR, "scarcely": B_DECR, "slightly": B_DECR, "somewhat": B_DECR, "sort of": B_DECR,
        "sorta": B_DECR, "sortof": B_DECR, "sort-of": B_DECR
    }
    SPECIAL_CASE_IDIOMS = {
        "the shit": 3, "the bomb": 3, "bad ass": 1.5, "yeah right": -2, "cut the mustard": 2, "kiss of death": -1.5,
        "hand to mouth": -2
    }

    REGEX_REMOVE_PUNCTUATION = re.compile(f"[{re.escape(string.punctuation)}]")
    PUNC_LIST = [".", "!", "?", ",", ";", ":", "-", "'", '"', "!!", "!!!", "??", "???", "?!?", "!?!", "?!?!", "!?!?"]

class SentimentAnalyzer:
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()
        self.constants = VaderConstants()

    def analyze_sentiment(self, text):
            sentiments = []
            words_and_emoticons = self._words_and_emoticons(text)
            for item in words_and_emoticons:
                valence = 0
                i = words_and_emoticons.index(item)
                if (i < len(words_and_emoticons) - 1 and item.lower() == "kind" and i + 1 < len(words_and_emoticons)):
                    if words_and_emoticons[i + 1].lower() == "of":
                        valence = 0
                    else:
                        valence = self._sentiment_valence(item)
                else:
                    valence = self._sentiment_valence(item)

                if i > 0 and words_and_emoticons[i - 1].lower() not in self.constants.BOOSTER_DICT:
                    # Previous word is not a booster, so negate the valence
                    valence = self._negate(valence, words_and_emoticons[i - 1])

                sentiments.append(valence)

            sentiments = self._sentiment_score_modifier(text, sentiments)
            return sentiments

    def _words_and_emoticons(self, text):
                # Remove punctuation except for word-emoticons like :), :-), ;), etc.
                text = self.constants.REGEX_REMOVE_PUNCTUATION.sub('', text)
                words_and_emoticons = text.split()
                return words_and_emoticons

    def _sentiment_valence(self, item):
                # Determine the valence of the item (word or emoticon)
                valence = 0
                item_lower = item.lower()
                if item_lower in self.analyzer.lexicon:
                    valence = self.analyzer.lexicon[item_lower]
                return valence

    def _negate(self, valence, preceding_item):
                # Negate the valence if the preceding word is a negation
                if preceding_item.lower() in self.constants.NEGATE:
                    valence *= self.constants.N_SCALAR
                return valence

    def _sentiment_score_modifier(self, text, sentiments):
                # Modify sentiment scores based on various rules
                words_and_emoticons = self._words_and_emoticons(text)
                for i in range(len(words_and_emoticons)):
                    if words_and_emoticons[i].lower() in self.constants.BOOSTER_DICT:
                        # Check for booster words
                        sentiment_mod = self.constants.BOOSTER_DICT[words_and_emoticons[i].lower()]
                        if i > 0 and words_and_emoticons[i - 1].lower() not in self.analyzer.lexicon:
                            # Previous word is not in lexicon, so apply booster to the preceding item
                            sentiments[i - 1] += sentiment_mod
                            sentiments[i - 1] = self._check_sentiment_mod(sentiments[i - 1])
                        if i < len(words_and_emoticons) - 1 and words_and_emoticons[
                            i + 1].lower() not in self.analyzer.lexicon:
                            # Next word is not in lexicon, so apply booster to the following item
                            sentiments[i + 1] += sentiment_mod
                            sentiments[i + 1] = self._check_sentiment_mod(sentiments[i + 1])
                return sentiments

    def _check_sentiment_mod(self, valence):
                # Check and adjust valence if it is greater than 2 or less than -2
                if valence > 2:
                    return 2
                elif valence < -2:
                    return -2
                else:
                    return valence