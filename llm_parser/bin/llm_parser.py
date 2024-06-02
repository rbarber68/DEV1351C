import sys,os
import glob
import base64
import requests as req
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
from splunklib.modularinput import *
import splunklib

class MyScript(Script):

    def get_scheme(self):
        # Returns scheme.
        scheme = Scheme("LLM Parser")
        scheme.use_external_validation = False
        scheme.use_single_instance = False
        scheme.description = "Parse a file using ML"

        folder = Argument("folder")
        folder.title = "Monitoring Folder"
        folder.data_type = Argument.data_type_string
        folder.description = "Folder (/opt/wav, /wav)"
        folder.required_on_create = True
        folder.required_on_edit = True
        scheme.add_argument(folder)
        
        provider = Argument("provider")
        provider.title = "Model Provider"
        provider.data_type = Argument.data_type_string
        provider.description = "Ollama, OpenAI, or Grok"
        provider.required_on_create = False
        provider.required_on_edit = False
        scheme.add_argument(provider)

        location = Argument("location")
        location.title = "Model Location"
        location.data_type = Argument.data_type_string
        location.description = "http://localhost:11434/api/generate, https://api.openai.com/v1/completions"
        location.required_on_create = False
        location.required_on_edit = False
        scheme.add_argument(location)

        model = Argument("model")
        model.title = "Model Name"
        model.data_type = Argument.data_type_string
        model.description = "GPT4, mistral, llava"
        model.required_on_create = False
        model.required_on_edit = False
        scheme.add_argument(model)

        prompt = Argument("prompt")
        prompt.title = "Prompt"
        prompt.data_type = Argument.data_type_string
        prompt.description = "What do you want to know?"
        prompt.required_on_create = False
        prompt.required_on_edit = False
        scheme.add_argument(prompt)
        return scheme
  
    def validate_input(self, validation_definition):
        pass

    def get_files_by_pattern(self, pattern):
        directory = os.path.dirname(pattern)
        if not os.path.exists(directory):
            return []

        # Use glob to find all files matching the pattern
        return glob.glob(pattern)
    
    def process_file(self, file, location, model, prompt):
        # Set the Ollama host and timeout
        #host = "localhost:11434"
        timeout = 60

        encoded_string = ""
        with open(file, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
        base64_string = encoded_string.decode('utf-8')

        # Create a request object
        request = req.post(
            location,
            json={"model": model, 
                "prompt": prompt, 
                "stream": False,
                "images": [str(base64_string)]},
            timeout=timeout,
        )

        # Get the response
        response = request.json()
        #return_string = response['response']
        response['formatted_response'] = response['response'].split("```json")[1].split("```")[0].strip("\n")
        # Print the response
        return response

    def stream_events(self, inputs, ew):
        for input_name,input_item in inputs.inputs.items():
            folder = input_item["folder"]
            prompt = input_item["prompt"]
            model = input_item["model"]
            location = input_item["location"]

            matching_files = self.get_files_by_pattern(folder)
            if matching_files:
                for file in matching_files:
                    response = self.process_file(file, location, model, prompt)
                    event = Event()
                    event.stanza = "ollama"
                    event.data = json.dumps(response)
                    ew.write_event(event)

if __name__ == "__main__":
    sys.exit(MyScript().run(sys.argv))

