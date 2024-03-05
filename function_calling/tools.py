import json

## Provide the instructiin for summary question to be passed to the prompt
def get_summary_instruction():
    instruction = "Carefully consider a walkthrough of all the messages in the provided conversion history. Present the list of topics in the conversation in numbered bullet points. Using this, answer the question."
    return {"instruction": instruction}

get_summary_instruction_description = """
            <tool_description>
            <tool_name>get_summary_instruction</tool_name>
            <description> It does not take any input parameter and returns instruction for conversation summary analysis question</description>
            </tool_description>
            """
 ## Provide the instruction for sentiment question to be passed to the prompt  
def get_sentiment_instruction():
    instruction = "Pay attention to the provided conversation history while answering the questions. Make sure you have sufficient data to back your reasoning when answering the question. The identified sentiment must be taken from these follwoing categories: Angry, Fearful, Happy, Neutral, Sad, Disgusted, Surprised, Curious to dive deeper. A conversation may contain mix of sentiment from the categories. Also make sure to provided reasoning behind your decision in bullet points"
    return {"instruction": instruction}
 
get_sentiment_instruction_description = """
            <tool_description>
            <tool_name>get_sentiment_instruction</tool_name>
            <description>
            It does not take any input parameter and returns instruction for conversation sentiment analysis question</description>
            </tool_description>
            """

## Provide the instructiin for general question to be passed to the prompt
def get_general_instruction():
    instruction = "Carefully consider all the messages in the provided conversion history. Using this, answer the question."
    return {"instruction": instruction}

get_general_instruction_description = """
            <tool_description>
            <tool_name>get_general_instruction</tool_name>
            <description> It does not take any input parameter and returns instruction for a general question where it is not about summary or sentiment</description>
            </tool_description>
            """

## Provide the conversation history as the context to the prompt
def get_conversation(id: str, question: str, instruction: str):
    with open('train.json', 'r') as f:
        data = json.load(f)
    return {"conversation": data[id]['content'], "question": question, "instruction": instruction}

    
get_conversation_description = """
            <tool_description>
            <tool_name>get_conversation</tool_name>
            <description>
            receive instruction from either get_sentiment_instruction_description or get_summary_instruction_description function and return instruction, user question and 1 JSON object containing the conversation history for the given conversation id.</description>
            <parameters>
            <parameter>
            <name>id</name>
            <type>string</type>
            <description>conversation id</description>
            </parameter>
            <parameter>
            <name>question</name>
            <type>string</type>
            <description>user question</description>
            </parameter>
            <parameter>
            <name>instruction</name>
            <type>string</type>
            <description>instruction</description>
            </parameter>
            </parameters>
            </tool_description>
            """
 
list_of_tools_specs = [
    get_general_instruction_description,
    get_summary_instruction_description,
    get_sentiment_instruction_description,
    get_conversation_description
    ]