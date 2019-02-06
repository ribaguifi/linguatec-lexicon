from django.db import models

from linguatec_lexicon import validators

class Lexicon(models.Model):
    """
    The Lexicon class provides a class to define a bilingual dictionary.

    Keep in mind that you define the Lexicon direction choosing the
    source and destination language. This direction is not
    bidirectional, so if you want to have a complete bilingual dictionary
    you have to create two Lexicon, one for each way.

    For example, a lexicon with Spanish as source language and
    Aragonese as destination language stores the translation in Aragonese
    for a collection of words in Spanish.

    """
    name = models.CharField(max_length=32)
    description = models.TextField(blank=True)
    # TODO use ISO 639 codes??? https://www.iso.org/iso-639-language-codes.html
    src_language = models.CharField(max_length=16)
    dst_language = models.CharField(max_length=16)

    def __str__(self):
        return self.name

# FIXME(@slamora) currently unused because search is implemented using
# django-rest-frameworks filters that provides a more powerfull search
# than using exact match.
class WordManager(models.Manager):
    def search(self, query):
        return self.filter(term=query)


class Word(models.Model):
    """
    The Word class stores each word (written in the source language)
    that compounds the Lexicon.

    """
    lexicon = models.ForeignKey('Lexicon', on_delete=models.CASCADE, related_name="words")
    term = models.CharField(unique=True, max_length=64)

    objects = WordManager()

    def __str__(self):
        return self.term

    def gramcats(self):
        return self.entries.values_list('gramcats__abbreviation', flat=True).distinct()


class Entry(models.Model):
    """
    The Entry class represents each translation (written in the
    destination language) for a word (written in the source language).

    """
    word = models.ForeignKey('Word', on_delete=models.CASCADE, related_name="entries")
    gramcats = models.ManyToManyField('GramaticalCategory', related_name="entries")
    translation = models.TextField()

    class Meta:
        verbose_name_plural = "entries"

    def __str__(self):
        return self.translation

class Example(models.Model):
    """
    The Example class stores examples of usage of a Entry.

    """
    entry = models.ForeignKey('Entry', on_delete=models.CASCADE, related_name="examples")
    phrase = models.TextField()

    def __str__(self):
        return self.phrase

class GramaticalCategory(models.Model):
    abbreviation = models.CharField(unique=True, max_length=32)
    title = models.CharField(max_length=128)

    class Meta:
        verbose_name_plural = "gramatical categories"

    def __str__(self):
        return self.abbreviation


class VerbalConjugation(models.Model):
    KEYWORD_MODEL = "modelo. conjug."
    KEYWORD_CONJUGATION = "conjug."

    entry = models.OneToOneField('Entry', on_delete=models.CASCADE, related_name="conjugation")
    raw = models.TextField('Raw imported content.')

    # TODO(@slamora) @cached property???
    def parse_raw(self):
        beg = None
        parsed = {}
        raw_lowcase = self.raw.lower()
        if self.KEYWORD_MODEL in raw_lowcase:
            # CASO 1
            beg = raw_lowcase.find(self.KEYWORD_MODEL)
            parsed["model"] = raw_lowcase[beg:].lstrip(self.KEYWORD_MODEL).strip()

        elif self.KEYWORD_CONJUGATION in raw_lowcase:
            # CASO 2A
            beg = raw_lowcase.find(self.KEYWORD_CONJUGATION)
            conjugation = validators.VerbalConjugationValidator()(self.raw)
            parsed["conjugation"] = conjugation

        parsed["intro"] = self.raw[:beg].strip()

        return parsed
