import os
import json
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Set the backend before importing pyplot
from django.shortcuts import render
from django.http.response import JsonResponse, HttpResponse
# from langchain import OpenAI, SQLDatabase
from langchain_community.llms import OpenAI
from langchain_community.utilities import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
from django.views.decorators.csrf import csrf_exempt
import io
import base64
import openai
# from langchain.document_loaders import PyPDFLoader, TextLoader
from langchain.document_loaders import TextLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain.vectorstores import FAISS
# from langchain.embeddings.openai import OpenAIEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.memory import ChatMessageHistory
from langchain.schema import messages_from_dict, messages_to_dict
import datetime
import uuid
from gtts import gTTS
# import playsound

openai.api_key = "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"
messages = []

# def text_to_speech(text, output_file):
#     tts = gTTS(text=text, lang='en')
#     tts.save(output_file)
# def play_audio(file_path):
#     playsound.playsound(file_path)

def chatPage(request):
    return render(request=request, context={'ans': "", 'prompt': ""}, template_name="index.html")

@csrf_exempt
def pdfApi(request):
    request_body = json.loads(request.body)
    user_in = request_body["messages"][0]["content"]
    chat_history = request_body['chat_history']
    if chat_history == []:
        chat_history = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    else:
        chat_history_dict = chat_history['chat_memory']['messages']
        chat_history = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        for i in range(0, len(chat_history_dict), 2):
                chat_history.save_context({"input": chat_history_dict[i]["content"]} , {"output": chat_history_dict[i + 1]["content"]})
        print(chat_history)
    
    apikey = "sk-proj-RzRIz5ZAsUVWAwINNmkjT3BlbkFJ5qSno9jv4RmVKkh1DKvs"
    os.environ['OPENAI_API_KEY'] = apikey
    
    # loader = PyPDFLoader("C:/Users/victo/Desktop/aychat/ay-chatbot/aychatbot/static/standalonechat/source_files/sample.pdf")
    # loader = TextLoader("C:/Users/victo/Desktop/aychat/ay-chatbot/aychatbot/static/standalonechat/source_files/text_sample.txt")
    # loader = PyPDFLoader("/Users/suhail270/Documents/GitHub/metaport-task/metaport/static/standalonechat/source_files/suhail.pdf")
    loader = PyPDFLoader("/Users/suhail270/Documents/GitHub/metaport-task/metaport/static/standalonechat/source_files/metaport.pdf")
    documents = loader.load()
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    documents = text_splitter.split_documents(documents)

    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma.from_documents(documents, embeddings)

    qa = ConversationalRetrievalChain.from_llm(OpenAI(temperature=0), vectorstore.as_retriever(), memory=chat_history)

    result = qa({"question": user_in})
    print(result)

    resp = result['answer']
    chat_history = chat_history.dict()
    print(chat_history) 

    # text_to_speech(resp,"output.mp3")

    # play_audio("output.mp3")

    return JsonResponse({"resp" : resp, "chat_history" : chat_history})


@csrf_exempt
def chatApi(request):
    # return JsonResponse({"resp" : "victor"}, safe=False)

    print(request.body)

    greetings = ["hey", "hello", "howdy", "sup", "what's up", "whats up",
                 "greetings", "wassup"]
    request_body = json.loads(request.body)
    user_in = request_body["messages"][0]["content"]

    if any(greeting in user_in.lower() for greeting in greetings):
        resp = "Hello! How can I help you?"
        return JsonResponse({"resp" : resp})
    
    if request_body["type"] == "pdf":
        return pdfApi(request)

    if ("graph" in user_in.lower()) or ("chart" in user_in.lower()) or ("plot" in user_in.lower()):
        return graphApi(request)
    
    apikey = "sk-proj-RzRIz5ZAsUVWAwINNmkjT3BlbkFJ5qSno9jv4RmVKkh1DKvs"
    os.environ['OPENAI_API_KEY'] = apikey
    
    # dburi = "sqlite:///testdb.sqlite3"
    dburi = request_body['db']
    db = SQLDatabase.from_uri(dburi)
    llm = OpenAI (temperature=0)
    db_chain = SQLDatabaseChain (llm=llm, database=db, verbose=True, use_query_checker=True, top_k=13)
    print(request_body)
    text = request_body['additional_prompt']
    # text = """\in the database names are stored in the following format: 
    #     "<lastname>,<firstname>" with no whitespace.
    #     the sql query should ignore all whitespace.
    #     the names in the answer should have the following format:
    #     "<firstname> <lastname>". """
    prompt = text + user_in
    resp = db_chain.run(prompt)
    
    # text_to_speech(resp,"output.mp3")

    # play_audio("output.mp3")
    
    return JsonResponse({"resp" : resp})

@csrf_exempt
def graphApi(request):
    request_body = json.loads(request.body)
    user_in = request_body["messages"][0]["content"]
    print(user_in)
    apikey = "sk-proj-RzRIz5ZAsUVWAwINNmkjT3BlbkFJ5qSno9jv4RmVKkh1DKvs"
    os.environ['OPENAI_API_KEY'] = apikey
    print(request_body)
    dburi = request_body['db']
    db = SQLDatabase.from_uri(dburi)
    llm = OpenAI (temperature=0)
    db_chain = SQLDatabaseChain (llm=llm, database=db, verbose=True, return_direct=True, return_intermediate_steps=True)
    text = request_body['additional_prompt']
    prompt = text + user_in
    resp = db_chain(prompt)
    sqlQuery = resp["intermediate_steps"][1]
    sqlresult = eval(resp["result"])
    queryy = "give me the columns names for teh following query in the form of a python list .only string please no explantions required and no human like answer just the list " + sqlQuery
    print(sqlQuery)
    messages.append({"role": "user", "content": queryy})
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    column_names = eval(response["choices"][0]["message"]["content"])

    x = []
    y = []

    for i in sqlresult:
        print(i)
        x.append(i[0])
        y.append(i[1])

    plt.clf()
    plt.bar(x, y)
    plt.xlabel(column_names[0])
    plt.ylabel(column_names[1])
    plt.xticks(rotation="vertical")
    plt.title('Graph from Query')
    plt.tight_layout()

    # plt.grid(True)
    # # Create a buffer to hold the image
    # buffer = io.BytesIO()

    # # Save the plot to the buffer
    # plt.savefig(buffer, format='png')
    # buffer.seek(0)

    # # Encode the image buffer as base64
    # image_base64 = base64.b64encode(buffer.getvalue()).decode()
    # print(image_base64)
    # # Build the HTML response with the image
    # html_response = '<img src="data:image/png;base64,{image_base64}" alt="Graph from SQL Query">'

    # # Close the buffer
    # buffer.close()

    # return HttpResponse(html_response)
    
    # Save the graph image to a BytesIO buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    # Convert the image to base64
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

    domain = request.get_host()

    # Generate the image URL
    img_id = uuid.uuid4().hex
    image_url = 'http://' + domain + '/static/graphs/graph' + str(img_id) + '.png'  # Assuming you have a 'static' folder in your Django project
    print(image_url)
    
    # Save the image as a static file
    image_path = os.path.join('static', 'graphs/graph' + str(img_id) + '.png')
    with open(image_path, 'wb') as f:
        f.write(base64.b64decode(image_base64))

    # Return the image URL in the JSON response
    return JsonResponse({"resp": image_url})
    # return JsonResponse({"resp": resp})
    
  

