# import re

# # Sample input string
# input_string = """ABBREVIATIONS ............................................................................. 51 
# CHAPTER 1 .................................................................................... 23
# OFFER DOCUMENT FOR SCHEMES ................................................ 17
# """

# # # Define a pattern to match the titles and page numbers
# # pattern = r'([A-Z\s]+)\.+(\d+)'
# pattern = r'([A-Z\s]+)\D*(\d+)'
# matches = re.findall(pattern, input_string)
# print(matches)


# # Convert matches into the desired format
# output = [(title.strip(), int(page)) for title, page in matches]

# print(output)
# content = ""
# result = []
# for i in input_string:
#     temp = []
#     if i.isalpha():
#         content += i
#     if i.isspace():
#         temp.append(content)
#     if i.isnumeric():
         
# for i in input_string.strip():
#     print(i)

# TODO: This code is to add section header on each page
##############
# import fitz  # PyMuPDF
# pdf_path = "./data/Master Circular for Mutual Funds.pdf"

# def add_headers_from_toc(pdf_path, output_path):
#     doc = fitz.open(pdf_path)
#     toc = []
#     # Extract TOC
#     for page in doc:
#         text = page.get_text()
#         if "INDEX" in text:
#             # Logic to parse TOC text and create a structured representation
#             toc = parse_toc(text)
#             break
#     # Add headers
#     for page in doc:
#         for heading in toc:
#             if page.number + 1 == heading["page"]:
#                 # Add heading to page
#                 page.insert_text((50, 50), heading["title"], fontsize=12)
#     doc.save(output_path)

# def parse_toc(text):
#     # Implement logic to parse TOC text and create a structured representation
#     # Example:
#     toc = []
#     for line in text.split("\n"):
#         if line.startswith("Chapter"):
#             title, page = line.split(" ")
#             toc.append({"title": title, "page": int(page)})
#     return toc

# # if __name__ == "__main__":
#     # add_headers_from_toc(filename, "output.pdf")

# doc = fitz.open(pdf_path)
# toc = []

# count = 0
# # Extract TOC
# for page in doc:
#     text = page.get_text()
#     if "INDEX" in text:
#         # Logic to parse TOC text and create a structured representation
#         # toc = parse_toc(text)
#         # print(text)
#         print("PAGE NUMBER: ", page.number + 1)
#         page_number = page.number
#         import re
#         # pattern = r'([A-Z\s]+).*(\d+)'
#         pattern = r'([A-Z\s]+)\D*(\d+)'
#         matches = re.findall(pattern, text)
#         print(matches)
#         count += 1
####################

def saved():
    print("saved.")