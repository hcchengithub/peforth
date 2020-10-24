# -*- coding: utf-8 -*-
# GitHub\gomforth\peforth_gom_port.py 
# This module is a modifier of peforth for GOM Inspect Suite.
# Usage: import gom, peforth, peforth_gom_port
# But we can modify a little and then run peforth_gom_port(2).py 
# directly to develop features and to debug.

import gom, peforth

# Input box dialog HTML composing

tips = '''
Break point example:
	if peforth.execute('debug').pop(): peforth.push(locals()).ok("bp>",cmd='to _locals_');
'exit' to close the input dialog. Run peforth.ok() to open it again.
Try 'help', 'help +', 'help -->', and 'words'.
'''

content = '<dialog>' \
	' <title>p e f o r t h	commnand line input box</title>' \
	' <style></style>' \
	' <control id="OkCancel"/>' \
	' <position>autometic</position>' \
	' <embedding>always_toplevel</embedding>' \
	' <sizemode>fixed</sizemode>' \
	' <size height="190" width="624"/>' \
	' <content rows="2" columns="2">' \
	'  <widget rowspan="1" type="label" columnspan="1" row="0" column="0">' \
	'	<name>label</name>' \
	'	<tooltip></tooltip>' \
	'	<text>_prompt_</text>' \
	'	<word_wrap>false</word_wrap>' \
	'  </widget>' \
	'  <widget rowspan="1" type="input::string" columnspan="1" row="0" column="1">' \
	'	<name>input</name>' \
	'	<tooltip></tooltip>' \
	'	<value></value>' \
	'	<read_only>false</read_only>' \
	'  </widget>' \
	'  <widget rowspan="1" type="label" columnspan="1" row="1" column="0">' \
	'	<name>label_1</name>' \
	'	<tooltip></tooltip>' \
	'	<text>Tips</text>' \
	'	<word_wrap>false</word_wrap>' \
	'  </widget>' \
	'  <widget rowspan="1" type="label" columnspan="1" row="1" column="1">' \
	'	<name>label_2</name>' \
	'	<tooltip></tooltip>' \
	'	<text>_text_</text>' \
	'	<wordwrap>false</wordwrap>' \
	'  </widget>' \
	' </content>' \
	'</dialog>'

content = content.replace("_text_",tips)

# Invoke the entity of a DIALOG
DIALOG = gom.script.sys.create_user_defined_dialog (content=content)

# Having the entity, make the trick to modify the prompt 
def dialog_event_handler (widget):
	DIALOG.label.text = peforth.dictate("py> vm.prompt").pop() or "OK "	 # get prompt 

DIALOG.handler = dialog_event_handler

# Dialog is ready, use it for the user input function 
def peforth_accept ():
	try:
		s = str(gom.script.sys.show_user_defined_dialog(dialog=DIALOG).input)
	except:
		s = "exit" # click cancel or press ESC
	return s

# Test 
# peforth_accept ()

# initialization 
peforth.push(peforth_accept).dictate(
	"""
	\ 設定適合 Gom 環境的 User Interface 
	constant peforth_accept // ( -- str ) python function get command line from a text dialog
	: accept peforth_accept :> () dup . cr ; // ( -- str ) A text dialog that reads a command line
	""")

# Test 
# peforth.ok("11> ")


