import stanza

def sent_info(sent):
    return [
        f"id: {word.id}\t"
        f"word: {word.text}\t"
        f"upos: {word.upos}\t"
        f"xpos: {word.xpos}\t"
        f"feats: {word.feats}\t"
        f"head id: {word.head}\t"
        f"head: {sent.words[word.head-1].text if word.head > 0 else 'root'}\t"
        f"deprel: {word.deprel}"
        for word in sent.words
    ]
    
    # return [word_info(w) for w in sent.words]

def doc_info(doc):
    return (sent_info(sent) for sent in doc.sentences) # 

def build_dep_printer(tokenize_pretokenized=True, pipeline=None):
    if not pipeline:
        pipeline = stanza.Pipeline(
            lang="en",
            processors="tokenize,pos,lemma,depparse,constituency",
            tokenize_pretokenized=tokenize_pretokenized,
        )
    def _(s):
        doc = pipeline(s)
        annot_doc = doc_info(doc)
        for idx, annot_sent in enumerate(annot_doc):
            print(f'====== Sentence {idx+1} =======')
            print(*annot_sent, sep="\n")
    return _

def main():
    pretok_prompt = "Are the sentences you will be providing already whitespace-tokenized? Enter any non-whitespace character(s) if they are; otherwise, just hit enter: "
    tokenize_pretokenized = bool(input(pretok_prompt).strip())
    print("tokenize_pretokenized: ", tokenize_pretokenized)
    pr = build_dep_printer(tokenize_pretokenized=tokenize_pretokenized)

    print(f"Enter sentence(s):\n")
    lines = []
    while True:
        try:
            lines.append(input())
        except EOFError:
            break
    pr("\n".join(lines))

if __name__ == "__main__":
    main()
