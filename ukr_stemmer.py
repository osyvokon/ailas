import re

class UkrainianStemmer():
     def __init__(self,word):
         self.word = word
         self.vowel = r'аеиоуюяіїє'  # http://uk.wikipedia.org/wiki/Голосний_звук
         self.perfectiveground = r'(ив|ивши|ившись|ыв|ывши|ывшись((?<=[ая])(в|вши|вшись)))$'
         self.reflexive = r'(с[яьи])$'  # http://uk.wikipedia.org/wiki/Рефлексивне_дієслово
         self.adjective = r'(ими|ій|ий|а|е|ова|ове|ів|є|їй|єє|еє|я|ім|ем|им|ім|их|іх|ою|йми|іми|у|ю|ого|ому|ої)$'  # http://uk.wikipedia.org/wiki/Прикметник + http://wapedia.mobi/uk/Прикметник
         self.participle = r'(ий|ого|ому|им|ім|а|ій|у|ою|ій|і|их|йми|их)$'  # http://uk.wikipedia.org/wiki/Дієприкметник
         self.verb = r'(сь|ся|ив|ать|ять|у|ю|ав|али|учи|ячи|вши|ши|е|ме|ати|яти|є)$'  # http://uk.wikipedia.org/wiki/Дієслово
         self.noun = r'(а|ев|ов|е|ями|ами|еи|и|ей|ой|ий|й|иям|ям|ием|ем|ам|ом|о|у|ах|иях|ях|ы|ь|ию|ью|ю|ия|ья|я|і|ові|ї|ею|єю|ою|є|еві|ем|єм|ів|їв|ю)$'  # http://uk.wikipedia.org/wiki/Іменник
         self.rvre = r'[аеиоуюяіїє]'
         self.derivational = r'[^аеиоуюяіїє][аеиоуюяіїє]+[^аеиоуюяіїє]+[аеиоуюяіїє].*(?<=о)сть?$'
         self.RV = ''

     def ukstemmer_search_preprocess(self,word):
         word = word.lower()
         word = word.replace("'","")
         word = word.replace(u"ё",u"е")
         word = word.replace(u"ъ",u"ї")

         return word

     def s(self,st, reg, to):
         orig = st
         self.RV = re.sub(reg, to, st)
         return (orig != self.RV)

     def stem_word(self):
          word = self.ukstemmer_search_preprocess(self.word)
          if not re.search(u'[аеиоуюяіїє]',word):
              stem = word
          else:
              p = re.search(self.rvre,word)
              start = word[0:p.span()[1]]
              self.RV = word[p.span()[1]:]

              # Step 1
              if not self.s(self.RV,self.perfectiveground,''):

                  self.s(self.RV,self.reflexive,'')
                  if self.s(self.RV,self.adjective,''):
                      self.s(self.RV,self.participle,'')
                  else:
                      if not self.s(self.RV,self.verb,''): self.s(self.RV,self.noun,'')
              # Step 2
              self.s(self.RV,u'и$','')

              # Step 3
              if re.search(self.derivational,self.RV):
                   self.s(self.RV,u'ость$','')

              # Step 4
              if self.s(self.RV,u'ь$',''):
                   self.s(self.RV,u'ейше?$','')
                   self.s(self.RV,u'нн$',u'н')

              stem = start + self.RV
          return stem