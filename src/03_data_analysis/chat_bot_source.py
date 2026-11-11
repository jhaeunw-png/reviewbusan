import os

import pandas as pd
from dotenv import load_dotenv

from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores.utils import DistanceStrategy
from langchain_huggingface import HuggingFaceEmbeddings

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import CommaSeparatedListOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI

# embeddings_model = HuggingFaceEmbeddings(
#     model_name='jhgan/ko-sbert-nli',
#     model_kwargs={'device':'cpu'},
#     encode_kwargs={'normalize_embeddings':True},
# )

from langchain_openai import OpenAIEmbeddings

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise RuntimeError("OPENAI_API_KEY 환경변수를 설정하세요.")

embeddings_model = OpenAIEmbeddings(
    model='text-embedding-3-small',
    openai_api_key=openai_api_key,
)
# 4. LLM 생성
chat = ChatOpenAI(
    model="gpt-6-sol",
    temperature=1,
    openai_api_key=openai_api_key,
)

# 1. CSV 읽기
df = pd.read_excel("회귀분석용_최종데이터.xlsx")
selected_cols = [
    "예측대상연월",
    "구군",
    "예측대상월_관광방문자수",
    "예측대상월_외지인방문자수",
    "예측대상월_외국인방문자수",
    "전월_관광방문자수",
    "전월_외지인방문자수",
    "전월_외국인방문자수"
]

df = df[selected_cols].copy()
# 3. Document 생성
documents = []

for idx, row in df.iterrows():

    content = "\n".join(
        f"{col}: {row[col]}"
        for col in df.columns
        if pd.notna(row[col])
    )

    documents.append(
        Document(
            page_content=content,
            metadata={
                "row": int(idx),
                "구군": str(row["구군"])
            }
        )
    )


# 4. FAISS 벡터 스토어 생성
vectorstore = FAISS.from_documents(
    documents=documents,
    embedding=embeddings_model,
    distance_strategy=DistanceStrategy.EUCLIDEAN_DISTANCE
)
# 저장
vectorstore.save_local("faiss_index-openai")

# 다시 불러오기
vectorstore = FAISS.load_local(
    "faiss_index-openai",
    embeddings_model,
    allow_dangerous_deserialization=True
)
# 5. Retriever 생성
retriever = vectorstore.as_retriever(
    search_kwargs={"k": 5}
)

# 2. OutputParser 생성
output_parser = CommaSeparatedListOutputParser()

format_instructions = output_parser.get_format_instructions()

# 3. 프롬프트 생성

prompt = PromptTemplate(
    template="""
다음은 특정 연월의 전체 구군 방문자 데이터입니다.

{context}

질문:
{question}

반드시 제공된 데이터를 기준으로 비교하여 답변하세요.
구군별 수치를 비교한 후 질문에 해당하는 구군명만 출력하세요.
데이터에 없는 내용은 추측하지 마세요.

{format_instructions}
""",
    input_variables=["context", "question"],
    partial_variables={
        "format_instructions":
            output_parser.get_format_instructions()
    }
)


# 5. 검색된 Document를 문자열로 변환
def format_docs(docs):
    return "\n".join(doc.page_content for doc in docs)

# 6. Chain 생성
chain = (
    {
        "context": retriever | format_docs,
        "question": RunnablePassthrough()
    }
    | prompt
    | chat
    | output_parser
)

# 7. 실행

result = chain.invoke(
    "2025년 12월 외지인 방문자 수가 가장 작은 구군은?"
)
print(result)
############
documents = []

for year_month, group in df.groupby("예측대상연월"):

    content = f"기준 연월: {year_month}\n\n"

    for _, row in group.iterrows():
        content += f"""
구군: {row['구군']}
관광 방문자 수: {row['예측대상월_관광방문자수']}
외지인 방문자 수: {row['예측대상월_외지인방문자수']}
외국인 방문자 수: {row['예측대상월_외국인방문자수']}
--------------------
"""

    documents.append(
        Document(
            page_content=content.strip(),
            metadata={
                "예측대상연월": str(year_month),
                "구군수": group["구군"].nunique()
            }
        )
    )


# 벡터 스토어 생성
vectorstore = FAISS.from_documents(
    documents=documents,
    embedding=embeddings_model
)

vectorstore.save_local("faiss_index-openai-v2")

# 다시 불러오기
vectorstore = FAISS.load_local(
    "faiss_index-openai-v2",
    embeddings_model,
    allow_dangerous_deserialization=True
)
# 검색
retriever = vectorstore.as_retriever(
    search_kwargs={"k": 1}
)

output_parser = CommaSeparatedListOutputParser()

prompt = PromptTemplate(
    template="""
다음은 특정 연월의 전체 구군 방문자 데이터입니다.

{context}

질문:
{question}

반드시 제공된 데이터를 기준으로 비교하여 답변하세요.
구군별 수치를 비교한 후 질문에 해당하는 구군명만 출력하세요.
데이터에 없는 내용은 추측하지 마세요.

{format_instructions}
""",
    input_variables=["context", "question"],
    partial_variables={
        "format_instructions":
            output_parser.get_format_instructions()
    }
)


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

chain = (
    {
        "context": retriever | format_docs,
        "question": RunnablePassthrough()
    }
    | prompt
    | chat
    | output_parser
)

result = chain.invoke(
    "2025년 12월 외지인 방문자 수가 가장 작은 구군은?"
)

print(result)
