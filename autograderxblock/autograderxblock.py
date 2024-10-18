"""TO-DO: Write a description of what this XBlock is."""

from importlib.resources import files
import pkg_resources
from web_fragments.fragment import Fragment
from xblock.core import XBlock
from xblock.fields import Integer, Scope, String, List
from django.template import Context, Template

import os
import requests
import json
import traceback
#from openai import OpenAI #TODO: ADD THIS TO REQUIREMENTS FOR XBLOCK!!

#Endpoints
def nebula_api_text_text_endpoint(document_text: str, prompt_text: str, max_length: int) -> str:
    """
    Sends a request to the API endpoint and returns the response.

    Args:
        document_path (str): Path to the document.
        prompt_text (str): The prompt text to be used for processing.
        max_length (int): Maximum length of the generated text.

    Returns:
        str: The generated text from the API.
    """
    #with open(document_path, 'r') as doc_file:
    #    document_text = doc_file.read()
    
    url = "http://ece-nebula09.eng.uwaterloo.ca:8000/generate"
    headers = {"Content-Type": "application/json"}
    data = {
        "prompt": f"{prompt_text}\n{document_text}",
        "max_length": max_length
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(data))
    response.raise_for_status()  # Raise an exception for HTTP errors
    return response.json()['response']

def phi_moe_api_text_text_endpoint(document_text: str, prompt_text: str, max_length: int) -> str:
    """
    Sends a request to the API endpoint and returns the response.

    Args:
        document_text (str): The document text to be processed.
        prompt_text (str): The prompt text to be used for processing.
        max_length (int): Maximum length of the generated text.

    Returns:
        str: The generated text from the API.
    """
    url = "http://ece-nebula16.eng.uwaterloo.ca:8000/generate"
    headers = {"Content-Type": "application/json"}
    data = {
        "prompt": f"{prompt_text}\n{document_text}",
        "max_length": max_length
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(data))
    response.raise_for_status()  # Raise an exception for HTTP errors
    
    # Parse the JSON response
    response_json = response.json()['response']
    #generated_text = response_json.get("response", "").strip()

    return response_json

#Aggregates
def text_text_eval(document_text:str,prompt_text: str,model: str = "nemo",max_length:int = 512,api_key = None) -> str:
    """
    Aggregates text generation from various API endpoints based on the specified model.

    Args:
        document_text (str): The input document text to be processed.
        prompt_text (str): The prompt text to guide the text generation.
        model (str, optional): The model to use for text generation ("gpt-4o-mini", "gpt-4o", "phi", or "nemo"). Defaults to "nemo".
        max_length (int, optional): The maximum length of the generated text. Defaults to 512.
        api_key (str, optional): The API key for models requiring authentication. Defaults to None.

    Returns:
        str: The generated text from the selected API.
    """
    if model == "phi":
        return phi_moe_api_text_text_endpoint(document_text,prompt_text,max_length)
    else:
        return nebula_api_text_text_endpoint(document_text,prompt_text,max_length)
    """
    if model == "gpt-4o-mini" or model == "gpt-4o":
        return openAI_text_text_endpoint(document_text,prompt_text,max_length=max_length,model=model,api_key = api_key)
    elif model == "phi":
        return phi_moe_api_text_text_endpoint(document_text,prompt_text,max_length)
    else:
        return nebula_api_text_text_endpoint(document_text,prompt_text,max_length)
    """
class AutograderXBlock(XBlock):
        
    #question_description = String(default="Enter the question description here", scope=Scope.settings)
    question_description = String(
        help="Description of the question",
        default="",
        scope=Scope.content
    )
     # TO-DO: delete count, and define your own fields.
    count = Integer(
        default=34, scope=Scope.content,
        help="A simple counter, to show something happening",
    )

    """
    rubric = List(default=[{"label": "meets expectations", "description": "", "weight": 0},
                           {"label": "does not meet expectations", "description": "", "weight": 0}],
                 scope=Scope.settings)
    """
    rubric = List(
        default=[{'label': 'Meets Expectations', 'description': '', 'weight': 0},
                 {'label': 'Does Not Meet Expectations', 'description': '', 'weight': 0}],
        scope=Scope.content,
        help="Editable rubric with labels and weights"
    )
    def render_template(self, template_path, context={}):
        template_str = self.resource_string(template_path)
        template = Template(template_str)
        return template.render(Context(context))
    
    def resource_string(self, path):
        """Helper to load a resource from the static directory."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")
    
    def studio_view(self, context):
        html = self.render_template("static/html/grading_xblock_studio.html",{'self':self,"question":self.question_description,'random_thing':self.count})
        frag = Fragment()
        frag.add_content(html)
        #frag = Fragment(html.format(self=self,question=self.question_description,random_thing=34))
        frag.add_css(self.resource_string("static/css/grading_xblock.css"))
        frag.add_javascript(self.resource_string("static/js/src/grading_xblock.js"))
        frag.initialize_js('GradingXBlockStudio')
        
        return frag

    @XBlock.json_handler
    def save_studio_data(self, data, suffix=''):
        # Save Studio data
        print("========================!!!!!!!!!!!!!!!!!!+================")
        
        self.question_description = data.get("question_description", "")
        self.rubric = data.get("rubric", [])
        return {"result": "success"}

    def student_view(self, context):
        html = self.render_template("static/html/grading_xblock_student.html",{'self':self})
        frag = Fragment()
        frag.add_content(html)
        #frag = Fragment(html.format(self=self,question=self.question_description,random_thing=34))
        frag.add_css(self.resource_string("static/css/grading_xblock.css"))
        frag.add_javascript(self.resource_string("static/js/src/grading_xblock.js"))
        frag.initialize_js('GradingXBlockStudent')
        
        return frag
        #html = self.resource_string("static/html/grading_xblock_student.html")
        #frag = Fragment(html.format(self=self))
        #frag = Fragment(html.format(self=self,question=self.question_description,random_thing=34))
        #frag.add_css(self.resource_string("static/css/grading_xblock.css"))
        #frag.add_javascript(self.resource_string("static/js/src/grading_xblock.js"))
        #frag.initialize_js('GradingXBlockStudent')
        #return frag

    @XBlock.json_handler
    def grade_submission(self, data, suffix=''):
        student_answer = data.get("student_answer", "")
        rubric = self.rubric  # Get the rubric that was saved
        rubric_string = self.format_rubric_for_grading(rubric)
        
        prompt = f"""You are helping to evaluate student work. The question you are evaluating is: {self.question_description}
        
        The rubric you are evaluating the work against is: {rubric_string}.
        
        You must produce two things: a label and a feedback string. The label must be exactly one of the labels supplied by the rubric. You must provide your label within <label> and </label> XML tags. The feedback must be based on the student answer and the label you chose. You must provide your feedback within <feedback> and </feedback> XML tags. You must not produce any other output. The student work is:
        
        {student_answer}
        
        """

        # Call the external evaluation function
        evaluation_string = text_text_eval(document_text=student_answer, prompt_text=prompt, model='nemo', max_length=1024)
        grade = 100
        print(evaluation_string)

        # Call grade computation function
        #grade = compute_grade(evaluation_string, [item['weight'] for item in rubric])

        # Save the student's grade
        self.runtime.publish(self, 'grade', {
            'value': grade,
            'max_value': 100,
        })

        return {
            "evaluation": evaluation_string,
            "grade": grade
        }

    def format_rubric_for_grading(self, rubric):
        # Format the rubric as needed for your external evaluation
        rubric_str = "\n".join([f"{item['label']}: {item['description']}" for item in rubric])
        return rubric_str
    # TO-DO: change this to create the scenarios you'd like to see in the
    # workbench while developing your XBlock.
    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("AutograderXBlock",
             """<autograderxblock/>
             """),
            ("Multiple AutograderXBlock",
             """<vertical_demo>
                <autograderxblock/>
                <autograderxblock/>
                <autograderxblock/>
                </vertical_demo>
             """),
        ]
