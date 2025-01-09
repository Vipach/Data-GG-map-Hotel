from openai_utils import OpenAIAssistant
from flask import Flask, request, jsonify, render_template

import json

app = Flask(__name__)
init_instruction = 'You will help me to read content of a post and suggest tags and name of the post.'
assistant = OpenAIAssistant(model_name='gpt-3.5-turbo-0125', init_instruction=init_instruction)

assistant_msg = 'Generate 3 to 5 keyword tags and suggest a best name that summarizes the given post content. Tags should focus on important keywords, tools, or methods mentioned in the content. Each tag should be lower case, contain a single word, or if composed of two words, should use a hyphen to connect them such as self-learning.\n'

# Detailed steps (if needed)
# assistant_msg += '# Steps\n'
# assistant_msg += '1. **Analyze Content**: Carefully read through the provided post content to identify key themes, tools, or methods.\n'
# assistant_msg += '2. **Identify Keywords**: Extract important keywords that represent the core ideas or topics discussed in the content.\n'
# assistant_msg += '3. **Create Tags**: Convert these keywords into simple, single-word tags or use hyphens to connect two-word tags.\n'
# assistant_msg += '4. **Summarize Content**: Suggest a concise name that effectively summarizes the essence of the post content.\n'
# assistant_msg += 'Notes\n'
# assistant_msg += '- Ensure that the suggested tags are relevant and capture the essence of the content.\n'
# assistant_msg += '- The content name should provide a clear summary without being too lengthy.\n'
# assistant_msg += '- The tags should provide a quick insight into the main topics covered.'

assistant.add_message('assistant', assistant_msg)

@app.route('/get_post', methods=['GET'])
def get_post_content():
    content = request.args.get('content')

    if not content:
        return jsonify({"error": "Missing required parameters"}), 400
    
    try:
        return ai_reader(content)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/cronjob', methods=['GET'])
def cronjob():
    return jsonify({"message": "Cronjob is running"})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/policy')
def policy():
    return render_template('policy.html')

def ai_reader(content):
    question = f'\nSuggest tags and name for the following post content based on the system instruction and assistant message: {content}\n'
    answer_format = '{"tags": ["tag1", "tag2", "tag3"], "name": "post name"}'
    response = assistant.answer(question, answer_format)
    print(response)
    return response

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
