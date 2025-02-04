from lollms.apps.console import Conversation 
import sys
from collections import deque
from pathlib import Path
import json
def flatten_json(json_obj, parent_key='', separator='.'):
    items = {}
    for k, v in json_obj.items():
        new_key = f"{parent_key}{separator}{k}" if parent_key else k
        if isinstance(v, dict):
            items.update(flatten_json(v, new_key, separator))
        else:
            items[new_key] = v
    return items

##  hack here to prepare the data
with open("prompts.json") as fi:
  modes = json.load(fi)

flatten=flatten_json(modes)

with open("flattened.json","w") as fo:
  json.dump(flatten,fo,indent=2,)

import re


def refactor_into_fiber_bundles(lines, bundle_size):
    bundles = []
    current_bundle = []
    
    for line in lines:
        # Split the line into fibers
        fibers = line.split('.')

        fibers = line.split('.')

        # Filter out empty lines or lines with only whitespace
        fibers = [fiber.strip() for fiber in fibers if re.search(r'\S', fiber)]

        # Add filtered fibers to the current bundle
        current_bundle.extend(fibers)
        
        # Check if the current bundle size exceeds the desired bundle size
        if len(current_bundle) >= bundle_size:
            # Add the current bundle to the list of bundles
            bundles.append(current_bundle)
            
            # Start a new bundle
            current_bundle = []
    
    # Add the last bundle if it's not empty
    if current_bundle:
        bundles.append(current_bundle)
    
    return bundles

class MyConversation(Conversation):
  def __init__(self, cfg=None):
    super().__init__(cfg, show_welcome_message=False)
    self.text_ring_buffer = deque()  # Ring buffer to hold user responses

  def read_input_file(self, file_path):
    with open(file_path, 'r') as file:
      lines = file.readlines()

      lines = refactor_into_fiber_bundles(lines, 2)
            
      for line in lines:
        self.text_ring_buffer.append(self.personality.user_message_prefix + "\n".join(line))



  def start_conversation2(self):
    count = 0
    while True:
      if not self.text_ring_buffer:
        print("No more user input to process.")
        return

      line = feed_text = self.text_ring_buffer.popleft()
      
      #print("You:", feed_text)            
      #print(self.personality.name + ": ", end="", flush=True)

      count = count + 1
      print("IL" + str(count) + " :" + line, flush=True)
      for name,key in flatten.items():
        print("DEBUG",name, key)
        output = self.safe_generate(key + line,
                                    callback=self.callback)
        print("OL" + str(count) + " " + name + " :: " + output.strip())
      #print()

  def callback(self, text, type=None, metadata: dict = {}):
    #print(text, end="")
    #sys.stdout.flush()
    return True

if __name__ == '__main__':
  cv = MyConversation(Path("config.yaml"))
  input_file_path = 'user_input.txt'
  cv.read_input_file(input_file_path)

  cv.start_conversation2()
