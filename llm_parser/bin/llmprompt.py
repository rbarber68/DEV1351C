from __future__ import absolute_import, division, print_function, unicode_literals
import os,sys
import time
import json
import requests as req
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
from splunklib.searchcommands import dispatch, GeneratingCommand, Configuration, Option, validators


@Configuration(type="reporting")
class llmprompt(GeneratingCommand):

    model = Option(require=True)
    prompt = Option(require=True)

    def process_file(self):
        # Set the Ollama host and timeout
        #host = "localhost:11434"
        timeout = 60
        location="http://localhost:11434/api/generate"
        
        # Create a request object
        request = req.post(
            location,
            json={"model": self.model, 
                "prompt": self.prompt, 
                "stream": False},
            timeout=timeout,
        )

        # Get the response
        response = request.json()
        return_string = response['response']
        # Print the response
        return return_string

    def generate(self):
        response = self.process_file()
        yield {'_time': time.time(),'test' : response}

dispatch(llmprompt, sys.argv, sys.stdin, sys.stdout, __name__)
