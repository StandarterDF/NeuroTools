import markdown_pdf

Name = input("Enter MD name: ")
Data = ""

with open(Name, "r", encoding="utf-8") as FileReader:
    Data = FileReader.read()

PDF = markdown_pdf.MarkdownPdf()
PDF.add_section(markdown_pdf.Section(Data, paper_size="A5"))
PDF.save("PDFConv_" + Name + ".pdf")