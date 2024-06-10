from __future__ import absolute_import, division, print_function, unicode_literals
import os,sys
import time
import json
import requests as req
import base64
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
from splunklib.searchcommands import dispatch, GeneratingCommand, Configuration, Option, validators


@Configuration(type="reporting")
class llmprompt(GeneratingCommand):

    model = Option(require=True)
    prompt = Option(require=True)
    file = Option(require=False)

    def process_file(self):
        # Set the Ollama timeout and location
        timeout = 60
        location="http://localhost:11434/api/generate"

        # Create a request object
        if self.file == None:
            request = req.post(
                location,
                json={"model": self.model, 
                    "prompt": self.prompt, 
                    "stream": False},
                timeout=timeout,
            )
        else:
            # Fetch the file via HTTP
            response = req.get(self.file)
            #response.raise_for_status()  # Ensure we notice bad responses
            # Encode the file content in base64
            encoded_string = base64.b64encode(response.content)
            base64_string = encoded_string.decode('utf-8')
            request = req.post(
                location,
                json={"model": self.model,
                    "prompt": self.prompt,
                    "stream": False,
                    "images": [str(base64_string)]},
                timeout=timeout,
            )
            
        # Get the response
        response = request.json()
        return_string = response['response']
        return return_string

    def generate(self):
        response = self.process_file()
        yield {'_time': time.time(),'reply' : response}

dispatch(llmprompt, sys.argv, sys.stdin, sys.stdout, __name__)
