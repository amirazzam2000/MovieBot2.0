import spacy
from spacy import displacy


class EntityAnalyzer:

    def __init__(self):
        self.sp = spacy.load('en_core_web_sm')

    def entity_analyzer(self, sentence):
        sentence = self.sp(sentence)
        for word in sentence:
            print(word.text, word.pos_, word.dep_, word.lemma_)

        for entity in sentence.ents:
            print(entity.text + ' - ' + entity.label_ + ' - ' + str(spacy.explain(entity.label_)))

        print("-------names-----------")
        for noun in sentence.noun_chunks:
            print(noun.text)


if __name__ == '__main__':
    entityAnalyzer = EntityAnalyzer()
    entityAnalyzer.entity_analyzer("The Avengers")
