from hazm import * 
import re


class org_extractor:
    
    DICT_PATH = 'resource/org/orgs.txt'
    TAGGER_PATH = 'resource/hazm_model/postagger.model'
    CHUNKER_PATH = 'resource/hazm_model/chunker.model'
    ROLES = ['NP', 'PP', 'VP', 'ADJP', 'ADVP']

    content = open(DICT_PATH, 'r+').readlines()
    normalizer = Normalizer()
    tagger = POSTagger(model=TAGGER_PATH)
    chunker = Chunker(model=CHUNKER_PATH)

    def __init__(self, text) -> None:
        self.txt = text
        self.text = self.normalizer.normalize(self.txt)

    def ngrams(self, text, n):
        words = text.split()
        ngrams = zip(*[words[i:] for i in range(n)])
        return [' '.join(ngram) for ngram in ngrams]

    def chunk_text(self):
        
        tagged = self.tagger.tag(word_tokenize(self.text))
        chunks = tree2brackets(self.chunker.parse(tagged))

        chunked = [[c.strip(), c.split()[-1]] for c in\
                    [re.sub(r'\.|،|]*|,|;|/|[۰-۹]+|\)|\(|-|«|»', '', chunk).strip() for chunk in chunks.split('[')] if len(c.split()) >= 2]

        for c in chunked:
            c[0] = c[0].replace('\u200c', ' ')

        roles_set = set(self.ROLES)

        for chunk in chunked:
            words = chunk[0].split()
            filtered_words = [word for word in words if word not in roles_set]

            chunk[0] = ' '.join(filtered_words)

            if chunk[1] not in roles_set:
                for word in words:
                    if word in roles_set:
                        chunk[1] = word 
                        break  

        return chunked

    def merge_np_chunks(self, chunked):
        nps, temp, id = [], '', 0

        while id < len(chunked):
            chunk = chunked[id]
            if chunk[1]=='NP':
                temp = chunk[0]
                while id<len(chunked)-1 and chunked[id+1][1]=='NP':
                    temp = temp + ' ' + chunked[id+1][0]
                    id = id + 1
                    
                else:
                    nps.append(temp)
                    temp = ''
            id= id+1

        return nps

    def make_ngrams(self, nps):
        ngs = []
        for np in nps:
            npg = []
            count = len(np.split())
            for i in range(count, 0, -1):
                npg.extend(self.ngrams(np, i))
            ngs.append(npg)

        return ngs
    
    def find_org(self):

        chunked = self.chunk_text()
        nps = self.merge_np_chunks(chunked=chunked)
        ngs = self.make_ngrams(nps=nps)
        
        output = []
        for row in ngs:
            t = []
            for ng in row: 
                if len(ng) < 4:
                    continue
                for org in self.content:
                    otp = re.match(f'^{ng}.*', org)

                    if isinstance(otp, re.Match):
                        t.append((otp))
            
            output.append(t)

        result = []
        for ng, otp in zip(ngs, output):
            for o in otp:
                mtch = o.group(0)
                if mtch in ng and mtch not in result and mtch in self.txt:
                    result.append(mtch)
        
        result = sorted(result, key=len, reverse=True)
        defined_terms = []
        for term in result:
            if not any(term in other[0] for other in defined_terms):
                for m in re.finditer(term, self.txt):
                    defined_terms.append((term, m.start(), m.end()))
        return defined_terms


text =  "عطف به نامه شماره ۹۱۹۲/۳۰۱۸۶ مورخ ۲۰/۲/۱۳۸۴ در اجرای اصل یکصد و بیست و سوم (۱۲۳) قانون اساسی جمهوری اسلامی ایران قانون مدیریت خدمات کشوری مصوب ۸/۷/۱۳۸۶ کمیسیون مشترک رسیدگی به لایحه مدیریت خدمات کشوری مجلس شورای اسلامی مطابق اصل هشتاد و پنجم (۸۵) قانون اساسی جمهوری اسلامی ایران که به مجلس شورای اسلامی تقدیم گردیده بود، پس از موافقت مجلس با اجرای آزمایشی آن به مدت پنج سال در جلسه علنی مورخ ۱۸/۱۱/۱۳۸۵ و تأیید شورای محترم نگهبان، به پیوست ارسال می گردد." 
ext = org_extractor(text)
print(ext.find_org())
