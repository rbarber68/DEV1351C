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
        scheme = Scheme("ML Parser")
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
    

    def  get_transcode(self, audio):
        import requests
        url = "http://127.0.0.1:5000/transcode?filename=" + audio
        response = requests.get(url=url)
        #print(response.text)
        return response.text

    def validate_input(self, validation_definition):
        # Validates input.
        pass

    def get_files_by_pattern(self, pattern):
        """
        Returns a list of file names that match a given pattern.

        Args:
        pattern (str): The path pattern to search for which can include wildcards.

        Returns:
        list: A list of file paths that match the pattern.
        """
        # Check if the directory part of the pattern exists
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
        return_string = response['response']
        # Print the response
        return response


    def stream_events(self, inputs, ew):
        # Splunk Enterprise calls the modular input, 
        # streams XML describing the inputs to stdin,
        # and waits for XML on stdout describing events.
        # {"input_stanza1" : {"api_key": value, "lang": value...},"input_stanza2" : {"api_key": value, "lang": value...}}
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
            

            '''
            if "model_size" in input_item:
                model_size = input_item["model_size"]
            else:
                model_size = "tiny"

            if "lang" in input_item:
                lang = input_item["lang"]
            else:
                lang = "en"

            '''
            #result, language, tag = self.get_transcode(audio_file)

            #for r in result["results"]:
            #    event = Event()
            #    event.stanza = input_name
            #    event.data = json.dumps(r)
            #    ew.write_event(event)


            #event = Event()
            #event.stanza = "test"
            #event.data = json.dumps(result)

            #event1 = Event()
            #event1.stanza = "test"
            #event1.data = "test"


            #ew.write_event(event)
            #ew.write_event(event1)

    def test_event(self):
        #set values
        #audio_file = "mypodcast_64kb.mp3"
        #audio_file = "Scarecrow_18_Baum_64kb.mp3"
        #audio_file = "arabicsampleexam_4.mp3"
        #audio_file = "English_Mastery_Formula.mp3"


        print(self.get_transcode(audio_file))

if __name__ == "__main__":
    sys.exit(MyScript().run(sys.argv))
    #MyScript().test_event()


