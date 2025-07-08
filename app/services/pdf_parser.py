from collections import Counter
import pdfplumber.pdf as pd


class PDFParser():
    """
    the format of the prompt will be: Quiz me using this book {book_title, book_metadata}, with the provided Text.
    Text = {text: {certain_text_chunk}, page_num: {page_number}, chapter: {chapter_name}, chapter_num:{chapter_number}
    """
    page_height: int
    cleaned_pdf: list
    text: dict
    vectors: list
    book_title: str
    skiped_intros = True
    paragraph_step: int

    chapter_name: str
    subsection_name: str


    # these are some standard mesures for element detection in the pdf
    header_size: int        # like Chapter number and title
    subheader_size: int     # Subsection at each chapter
    normal_size: int        # paragrapgh/normal text
    footnote_size: int      # head/foot/keynote of the page

    STARTING_KEYWORDS = [
        'Chapter 1',
        'Introduction',
        '1 .Introduction'
        '1.Introduction'
        '1. Introduction'
    ]

    def __init__(self, pdf_path, header=16, subheader=15, normal=12, footer=8):
        try:
            self.chapter_name = str()
            self.vectors = []
            self.text = {}
            self.cleaned_pdf = []
            file = open(pdf_path, "rb")
            self.pdf = pd.PDF(file)
            self.page_height = self.pdf.pages[0].height
            self.header_size = header
            self.subheader_size = subheader
            self.normal_size = normal
            self.footnote_size = footer
            # self.get_pargraph_step(test_page=22)
            self.extract_first_page_metadata()
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            exit()

    def get_pargraph_step(self, test_page):
        sizes = []
        changes = []
        page = self.pdf.pages[test_page]
        for t in page.extract_words(extra_attrs=['size']):
            if t['size'] < self.normal_size and t['size'] > self.footnote_size:
                sizes.append(t['top'])
        vals = sorted(set(sizes))
        i = 0
        while i < len(vals) - 1:
            changes.append(int(vals[i + 1] - vals[i]))
            i += 1
        self.paragraph_step = Counter(changes).most_common(1)[0][0]

    def extract_first_page_metadata(self):
        page = self.pdf.pages[0].extract_words(extra_attrs=['size'])
        sizes = sorted(set([t['size'] for t in page]), reverse=True)
        metadata = []
        for s in sizes:
            metadata.append(
                " ".join(
                    [t['text']
                        for t in page if t['size'] == s and t['size'] > 10.0]
                )
            )
        self.book_title = metadata[0]
        self.book_metadata = metadata[1:]

    def clean_text_book(self):
        i = 1
        for p_stream in self.pdf.pages:
            page = p_stream
            clean_page = self.clean_page(page)
            if clean_page:
                self.get_token(clean_page, i)
            i += 1

    def clean_page(self, page):
        for key in self.STARTING_KEYWORDS:
            if not self.skiped_intros:
                break
            if key in [t['text'] for t in page.extract_text_lines(return_chars=False)]:
                self.skiped_intros = False
        if self.skiped_intros:
            return None
        text = page.extract_text_lines(x_tolerance=1)
        return [p for p in text if p['top'] > 0.1 * self.page_height]

    def get_token(self, page, page_num):
        # store each chapter Name
        # store each subsection
        # use text size to get diffirent component

        chapter_name = []
        subsection = []
        paragraphs = []
        is_chapter_found = False
        is_subsection_found = False

        for line in page:
            if any(char.get('size') > 15 for char in line['chars']):
                is_chapter_found = True
                chapter_name.append(line['text'])
            elif any(char.get('size') > 12 for char in line['chars']):
                is_subsection_found = True
                if len(subsection) > 1:
                    subsection.clear()
                subsection.append(line['text'])
                if len(paragraphs):
                    self.append_data(chapter_name, subsection[0], paragraphs, page_num)
                    paragraphs.clear()
            elif any(char.get('size') > 9 for char in line['chars']):
                paragraphs.append(line['text'].strip())

        if is_chapter_found:
            self.chapter_name = " ".join(chapter_name)
        if is_subsection_found:
            self.subsection_name = " ".join(subsection)
        self.append_data(self.chapter_name, self.subsection_name, paragraphs, page_num)

    def append_data(self, chapter_name, subsection_name, text, pn):
        chapter = "".join(chapter_name)
        if not len(chapter):
            chapter = self.chapter_name
        metadata = {}
        metadata['page_number'] = pn
        metadata['book_title'] = self.book_title
        metadata['chapter_name'] = chapter
        metadata['subsection_name'] = "".join(subsection_name)
        paragrapgh = " ".join(text)
        self.text['metadata'] = metadata
        self.text['text'] = paragrapgh
        self.vectors.append(self.text.copy())
