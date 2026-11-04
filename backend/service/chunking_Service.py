from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_into_chunks(text:str):


    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        separators=["\n\n", "\n", " ", ""]
    )

    chunks = text_splitter.split_text(text)

    return chunks