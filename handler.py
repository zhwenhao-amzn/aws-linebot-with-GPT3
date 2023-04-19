import json
import os
import openai
import boto3
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from transformers import GPT2Tokenizer

#os.environ['TRANSFORMERS_CACHE'] = '/tmp/transformers_cache'
#os.environ['HF_HOME'] = '/tmp/huggingface'

# Set up your OpenAI API key and LINE bot API credentials
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
LINE_CHANNEL_SECRET = os.environ['LINE_CHANNEL_SECRET']
LINE_CHANNEL_ACCESS_TOKEN = os.environ['LINE_CHANNEL_ACCESS_TOKEN']

# Initialize the OpenAI API client and DynamoDB resource
openai.api_key = OPENAI_API_KEY
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('line_bot_conversations')

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

def lambda_handler(event, context):
    headers = {k.lower(): v for k, v in event['headers'].items()}
    signature = headers['x-line-signature']
    body = event['body']

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return {
            'statusCode': 400,
            'body': json.dumps('Invalid signature. Check your channel secret.')
        }

    return {'statusCode': 200, 'body': json.dumps('OK')}

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    user_text = event.message.text

    # Retrieve the conversation history from DynamoDB
    conversation = get_conversation(user_id)

    # Update the conversation history
    conversation += f"User: {user_text}\n"

    # Call the OpenAI API to generate a response
    gpt_response = call_openai_gpt(conversation)

    # Update the conversation history with the bot's response
    conversation += f"Bot: {gpt_response}\n"

    # Save the updated conversation history to DynamoDB
    save_conversation(user_id, conversation)

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=gpt_response)
    )


def call_openai_gpt(conversation):
    #openai.api_key = os.environ['OPENAI_API_KEY']
    model_engine = "text-davinci-003"

    tokenizer = GPT2Tokenizer.from_pretrained("gpt2", cache_dir='/tmp/transformers_cache')

    tokens = tokenizer.encode(conversation)
    if len(tokens) > 2048:
        tokens = tokens[-2048:]

    prompt = tokenizer.decode(tokens)

    response = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.8,
    )

    message = response.choices[0].text.strip()
    return message


def get_conversation(user_id):
    response = table.get_item(Key={'user_id': user_id})
    if 'Item' in response:
        return response['Item']['conversation']
    return ""

def save_conversation(user_id, conversation):
    table.put_item(Item={
        'user_id': user_id,
        'conversation': conversation
    })
