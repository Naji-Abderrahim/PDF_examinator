from fastapi import APIRouter
from app.services.pdf_parser import PDFParser
# from app.models.schemas import ParseRequest, ParseResponse

router = APIRouter()


@router.get("/hi/{item}")
def parse_pdf(item: int):
    return {"Message": item}
    # parser = PDFParser(data.pdf.path)
    # result = parser.book_title
    # return {"content": result}
#
# @router.post("/parse-pdf", response_model=ParseResponse)
# def parse_pdf(data: ParseRequest):
#     parser = PDFParser(data.pdf.path)
#     result = parser.book_title
#     return {"content": result}
