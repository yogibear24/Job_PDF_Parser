import io
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfpage import PDFPage
import re
import glob
import numpy as np
import pandas as pd
# Using as much Python as possible, no Java or C++ required like Tabula, Tika, etc.

def extract_string_from_pdf(pdf_path):
    resource_manager = PDFResourceManager() # Function to store shared resources such as fonts and images
    fake_file_handle = io.StringIO() #
    converter = TextConverter(resource_manager, fake_file_handle)
    page_interpreter = PDFPageInterpreter(resource_manager, converter) # Function used to process the page contents
    with open(pdf_path, 'rb') as fh:
        for page in PDFPage.get_pages(fh, caching=True, check_extractable=True):
            page_interpreter.process_page(page)
        text = fake_file_handle.getvalue()
    # close open handles
    converter.close()
    fake_file_handle.close()
    if text:
        return text

def parse_pdf_string_to_list(pdf_as_string):
    string_indices_to_split = [0]
    new_string = pdf_as_string.strip("12/#ForceCode#ForceCode")
    for string_index in range(1, len(new_string) - 2):
        if new_string[string_index].isalpha() is not True and new_string[string_index + 1].isalpha() is True:
            string_indices_to_split.append(string_index + 1)
        elif new_string[string_index - 1].isalpha() is True and new_string[string_index].isalpha() is not True:
            string_indices_to_split.append(string_index + 1)
            # TODO: Include rules for conjoined alphabetical characters
    string_list = [new_string[i:j] for i, j in zip(string_indices_to_split, string_indices_to_split[1:] + [None])]
    return(string_list)

def transform_folder_to_lists(folder_path):
    folder_as_list = glob.glob(folder_path)
    pdf_strings = []
    for pdf_index in range(0, len(folder_as_list)):
        pdf_strings.append(extract_string_from_pdf(folder_as_list[pdf_index]))
    pdf_string_list_of_lists = []
    for string_index in range(0, len(pdf_strings)):
        pdf_string_list_of_lists.append(parse_pdf_string_to_list(pdf_strings[string_index]))
    return(pdf_string_list_of_lists)

#testing_three = transform_folder_to_lists("C:/Users/Everet/Documents/Projects/pdf_parser/Test_Data/*.pdf")
#print(testing_three[0])
#print(testing_three[1])
#print(testing_three[2])
#print(testing_three[3])

def get_role_and_job_id(pdf_string_list):
    job_id = pdf_string_list[pdf_string_list.index("jobs/") + 1].strip("/")
    role_to_join = []
    role_in_seq = False
    for string_index in range(0, len(pdf_string_list)):
        if pdf_string_list[string_index] == "- " and pdf_string_list[string_index - 1] == "Alliance ":
            role_in_seq = True
        elif role_in_seq is True and pdf_string_list[string_index] == "in ":
            role_in_seq = False
        elif role_in_seq is True and pdf_string_list[string_index] == " ":
            role_in_seq = False
        elif role_in_seq is True:
            role_to_join.append(pdf_string_list[string_index])
    role = "".join(list(dict.fromkeys(role_to_join))).strip(",")
    return(role, job_id)

def transform_lists_to_dataframe(list_of_pdf_string_list):
    role_list = []
    job_id_list = []
    for list_index in range(0, len(list_of_pdf_string_list)):
        role_list.append(get_role_and_job_id(list_of_pdf_string_list[list_index])[0])
        job_id_list.append(get_role_and_job_id(list_of_pdf_string_list[list_index])[1])
    pdf_dataframe = pd.DataFrame(np.column_stack([role_list, job_id_list]), columns=["Role", "Job ID"])
    return(pdf_dataframe)

def create_dataframe_from_folder(folder_path):
    pdfs_as_lists = transform_folder_to_lists(folder_path)
    pdfs_as_dataframe = transform_lists_to_dataframe(pdfs_as_lists)
    return(pdfs_as_dataframe)

testing_seven = create_dataframe_from_folder("C:/Users/Everet/Documents/Projects/pdf_parser/Test_Data/*.pdf")
print(testing_seven)




