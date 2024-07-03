import streamlit as st
import pandas as pd
from vertexai.generative_models import GenerativeModel
from vertexai.language_models import TextEmbeddingModel, TextEmbeddingInput
from google.cloud import bigquery
import logging
import json

project_id = "elite-air-423414-h9"
dataset_id = "testdata"
table_id = "employee"

def get_bigquery_description():
    try:
        client = bigquery.Client()
        QUERY = f'SELECT * FROM `{project_id}.{dataset_id}.INFORMATION_SCHEMA.TABLES` WHERE table_name = "{table_id}"'
        query_job = client.query(QUERY)
        rows = query_job.result()
        for row in rows:
            return row
    except Exception as e:
        logging.error(f"Error: {e}")
        return str(e)

def execute_query(query):
    try:
        client = bigquery.Client()
        query_job = client.query(query)
        rows = query_job.result()
        result = []
        for row in rows:
            result.append(row)
        return result
    except Exception as e:
        logging.error(f"Error: {e}")
        return str(e)

import vertexai
from vertexai.generative_models import GenerativeModel, Part, FinishReason
import vertexai.preview.generative_models as generative_models

def generate_answer(question, answer):
    vertexai.init(project="elite-air-423414-h9", location="us-central1")
    model = GenerativeModel(
        "gemini-1.0-pro-002", system_instruction=["""You are a helpful assistant."""]
    )
    responses = model.generate_content(
        [f"""User Question: {question}\n\nBigQuery results: {answer}, please summarize the results."""],
        generation_config=generation_config,
        safety_settings=safety_settings,
        stream=True,
    )
    response_text = ""
    for response in responses:
        response_text += response.text
    return response_text

generation_config = {
    "max_output_tokens": 2048,
    "temperature": 0,
    "top_p": 1,
}

safety_settings = {
    generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
}

def generate_query(question):
    vertexai.init(project="elite-air-423414-h9", location="us-central1")
    model = GenerativeModel(
        "gemini-1.0-pro-002",
        system_instruction=[f"""You are a BigQuery Expert and you are designed to generate SQL queries for a given user question. Here is the table description for the table {table_id}: \n\n\n {description}. Your response should be in JSON format, for example: \n\n\n {{"query": "SELECT * FROM `fresh-span-40021.chetan_test_dataset.employees`", "description": "This query will return all the records from the table"}}"""]
    )
    responses = model.generate_content(
        [question],
        generation_config=generation_config,
        safety_settings=safety_settings,
        stream=False,
    )
    response = responses.text
    response = response.replace("```json", "").replace("```", "")
    response = json.loads(response)
    query = response["query"]
    return query

description = get_bigquery_description()

# Streamlit 
st.title("BigQuery Chatbot")

question = st.text_input("Enter your question:")

if st.button("Enter"):
    if question:
        query = generate_query(question)
        result = execute_query(query)
        answer = generate_answer(question, result)
        st.write(f"Answer: {answer}")
    else:
        st.write("Please enter a question.")
