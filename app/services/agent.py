from langchain_core.documents import Document


class AgentDocument():
    def __init__(self, book_data):
        self.document = []
        for item in book_data:
            data = Document(page_content=item['text'], metadata=item['metadata'])
            self.document.append(data)
