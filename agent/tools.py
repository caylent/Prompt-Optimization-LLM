import json
import boto3

def summary_gen_tool():
    """
    Use this tool only to return instruction for conversation summary analysis question before calling get_conversation() tool. The input is the customer's question.
    """

    instruction = "Carefully consider a walkthrough of all the messages in the provided conversion history. Present the list of topics in the conversation in numbered bullet points. Using this, answer the question."
    return instruction

def sentiment_gen_tool():
    """
    Use this tool only to return instruction for conversation sentiment analysis question before calling get_conversation() tool. The input is the customer's question.
    """

    instruction = "Pay attention to the provided conversation history while answering the questions. Make sure you have sufficient data to back your reasoning when answering the question. The identified sentiment must be taken from these follwoing categories: Angry, Fearful, Happy, Neutral, Sad, Disgusted, Surprised, Curious to dive deeper. A conversation may contain mix of sentiment from the categories. Also make sure to provided reasoning behind your decision in bullet points"
    return instruction


def other_question_gen_tool():
    """
    Use this tool only to return instruction for a general question where it is not about summary or sentiment before calling get_conversation() tool. The input is the customer's question.
    """

    instruction = "Carefully consider all the messages in the provided conversion history. Using this, answer the question."
    return instruction



def get_conversation_tool(id, question, instruction):
    """
    Use this tool to receive instruction from either summary_gen_tool or sentiment_gen_tool or general_gen_tool function and return instruction, user question and 1 JSON object containing the conversation history for the given conversation id.
    """
    s3_bucket = '131578276461-us-east-1-secure-mlops'
    file_key = 'train.json'

    s3 = boto3.client('s3')

    response = s3.get_object(Bucket=s3_bucket, Key=file_key)
    f = response['Body'].read().decode('utf-8')
    data = json.loads(f)

    conversation_history = data[id]['content']

    return {"conversation": conversation_history, "question": question, "instruction": instruction}

