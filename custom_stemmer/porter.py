import re


class Stemmer():
    PERFECTIVEGROUND = re.compile(u"((ив|ивши|ившись|ыв|ывши|ывшись)|((?<=[ая])(в|вши|вшись)))$")
    REFLEXIVE = re.compile(u"(с[яь])$")
    ADJECTIVE = re.compile(u"(ее|ие|ые|ое|ими|ыми|ей|ий|ый|ой|ем|им|ым|ом|его|ого|ему|ому|их|ых|ую|юю|ая|яя|ою|ею)$")
    PARTICIPLE = re.compile(u"((ивш|ывш|ующ)|((?<=[ая])(ем|нн|вш|ющ|щ)))$")
    VERB = re.compile(
        u"((ила|ыла|ена|ейте|уйте|ите|или|ыли|ей|уй|ил|ыл|им|ым|ен|ило|ыло|ено|ят|ует|уют|ит|ыт|ены|ить|ыть|ишь|ую|ю)|((?<=[ая])(ла|на|ете|йте|ли|й|л|ем|н|ло|но|ет|ют|ны|ть|ешь|нно)))$")
    NOUN = re.compile(
        u"(а|ев|ов|ие|ье|е|иями|ями|ами|еи|ии|и|ией|ей|ой|ий|й|иям|ям|ием|ем|ам|ом|о|у|ах|иях|ях|ы|ь|ию|ью|ю|ия|ья|я)$")
    RVRE = re.compile(u"^(.*?[аеиоуыэюя])(.*)$")
    DERIVATIONAL = re.compile(u".*[^аеиоуыэюя]+[аеиоуыэюя].*ость?$")
    DER = re.compile(u"ость?$")
    SUPERLATIVE = re.compile(u"(ейше|ейш)$")
    I = re.compile(u"и$")
    P = re.compile(u"ь$")
    NN = re.compile(u"нн$")

    def stem(self, word):
        word = word.lower()
        word = word.replace(u'ё', u'е')  # this letters are equal according to algorithm
        m = re.match(Stemmer.RVRE, word)

        if not m or not m.groups():
            return word

        pre = m.group(1)
        rv = m.group(2)

        # step 1
        temp = Stemmer.PERFECTIVEGROUND.sub('', rv, 1)
        if temp == rv:
            rv = Stemmer.REFLEXIVE.sub('', rv, 1)
            temp = Stemmer.ADJECTIVE.sub('', rv, 1)
            if temp != rv:
                rv = temp
                rv = Stemmer.PARTICIPLE.sub('', rv, 1)
            else:
                temp = Stemmer.VERB.sub('', rv, 1)
                if temp == rv:
                    rv = Stemmer.NOUN.sub('', rv, 1)
                else:
                    rv = temp
        else:
            rv = temp

        # step 2
        rv = Stemmer.I.sub('', rv, 1)

        # step 3
        if re.match(Stemmer.DERIVATIONAL, rv):
            rv = Stemmer.DER.sub('', rv, 1)

        # step 4
        temp = Stemmer.P.sub('', rv, 1)
        if temp == rv:
            rv = Stemmer.SUPERLATIVE.sub('', rv, 1)
            rv = Stemmer.NN.sub(u'н', rv, 1)
        else:
            rv = temp
        word = pre + rv
        return word