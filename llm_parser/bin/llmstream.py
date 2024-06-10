import os,sys
import requests as req
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
from splunklib.searchcommands import dispatch, StreamingCommand, Configuration, Option, validators


@Configuration()
class llmstream(StreamingCommand):

    model = Option(require=True)
    prompt = Option(require=True)
    evalfieldname = Option(require=True)
    fieldname = Option(require=True)
    
    def process_file(self, field_data):
        timeout = 60
        location="http://localhost:11434/api/generate"
        
        # Create a request object
        request = req.post(
            location,
            json={"model": self.model, 
                "prompt": self.prompt + "\r\r" + field_data, 
                "stream": False},
            timeout=timeout,
        )

        # Get the response
        response = request.json()
        return_string = response['response']
        # Print the response
        return return_string
    
    def stream(self, events):
       for event in events:
           response = self.process_file(event[self.evalfieldname])
           event[self.fieldname] = response
           yield event

dispatch(llmstream, sys.argv, sys.stdin, sys.stdout, __name__)
