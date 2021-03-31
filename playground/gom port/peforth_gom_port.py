# -*- coding: utf-8 -*-
# GitHub\gomforth\peforth_gom_port.py
# This module is a modifier of peforth for GOM Inspect Suite.
# Usage: import gom, peforth, peforth_gom_port
# But we can modify a little and then run peforth_gom_port(2).py
# directly to develop features and to debug.

#
# 注意！ 以下是 Gom python 特有的問題：
#   1. ''' 裡面不能有 <something> 像 HTML tag 的東西，至少要成對。 '''
#   2. print("\n abc \n") 不能有 \n 
#   3. 
#

import gom, peforth

# Input box dialog HTML composing

tips = '''
Example low level breakpoint: ( High level simply *debug* prompt )
  peforth.bp(22,locals())  # drop breakpoint 22
Breakpoint commands:  bl  be  bd  be*  bd*  (try " help bl " )
'exit' or ESC leaves the breakpoint and continue running.
'bye' to totally stop the script session.
'''

content = '<dialog>' \
	' <title>p e f o r t h	 Commnand Line Input Box</title>' \
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

def bp(id=None,locals=None):
	if id==None: 
		id = 0
		prompt='bp> '
	else:
		prompt="{}>".format(id)
	if id in peforth.bps: peforth.push(locals).ok(prompt, cmd="to _locals_")
peforth.bp = bp
peforth.push(bp).dictate("py: vm.bp=pop()")
peforth.bps = [i for i in range(1000)]

# initialization
peforth.push(peforth_accept).dictate(
	"""
	\ 設定適合 Gom 環境的 User Interface
		constant peforth_accept // ( -- str ) python function get command line from a text dialog
		: accept peforth_accept :> () dup . cr ; // ( -- str ) A text dialog that reads a command line
		import time \ time :> sleep(1) 暫停一秒鐘

	\ 把 gom 變成 peforth 裡的 python global
		gom	 py: vm.gom=pop()
		char Part value part // ( -- 'Part' ) 通常是 'Part' 也有 'X+', 'Z-' 的時候。

	code words # ( <pattern> -- ) List all words, in the active vocabularies, with the pattern in their name. Modified for Gom to wrap a long line.
		pattern = nexttoken('\\n|\\r').strip() # avoid selftest to read TIB too much
		if pattern:		   # ^^^^^^^ 這個地方 debug 好久, 放進 peforth.gom.port.py 是在 python string 裡面，要改成 doulbe backslash
			screened = [w.name for w in words['forth'][1:] if w.name.find(pattern)!=-1]
		else:
			screened = [w.name for w in words['forth'][1:]]
		j = 0
		for i in screened:
			print(i, end=" ")
			j += 1
			if j % 10 == 0 : print()
		print()
		end-code
		/// Examples of listing screened words:
		/// 1.List all code words
		///	  <py> [w.name for w in words['forth'][1:] if 'code' in w.type] </pyV>
		/// 2.List all words that have not passed their own selftest
		///	  <py> [w.name for w in words['forth'][1:] if 'pass'!=getattr(w,'selftest',False)] </pyV>
		/// 3.List all words that have 'Cast' in their name, help, or comment
		///	  <py> eval("[w.name for w in words['forth'][1:] if (w.name.find('{{0}}')!=-1 or w.help.find('{{0}}')!=-1 or w.comment.find('{{0}}')!=-1)]".format('Cast'))</pyV>

	: msgbox // ( "message" -- ) Pop up a message box
		<py>
		DIALOG=gom.script.sys.create_user_defined_dialog (content='<dialog>' \
		' <title>使用說明</title>' \
		' <style></style>' \
		' <control id="Close"/>' \
		' <position>automatic</position>' \
		' <embedding>always_toplevel</embedding>' \
		' <sizemode>fixed</sizemode>' \
		' <size height="50" width="260"/>' \
		' <content rows="1" columns="1">' \
		'  <widget row="0" rowspan="1" columnspan="1" column="0" type="label">' \
		'	<name>label</name>' \
		'	<tooltip></tooltip>' \
		'	<text>這裡是 label.text </text>' \
		'	<word_wrap>false</word_wrap>' \
		'  </widget>' \
		' </content>' \
		'</dialog>')
		def dialog_event_handler (widget):
			pass
		DIALOG.handler = dialog_event_handler
		# peforth.ok("11> ",cmd="to _locals_") #  DIALOG :: label.text="abc"
		DIALOG.label.text=pop()
		RESULT=gom.script.sys.show_user_defined_dialog (dialog=DIALOG)
		</py> ;

	: objectview // ( dict -- objview ) Convert a dict to an objectview
		\ https://goodcode.io/articles/python-dict-object/
		\ https://medium.com/swlh/jdict-javascript-dict-in-python-e7a5383939ab
		<py>
			class objectview(object):
				def __init__(self, d):
					self.__dict__ = d
			o = objectview(pop())
			push(o)
		</py> ;
		/// py> {"x":11} objectview :> x # access x directly instead of ['x']

	: view24 // ( -- ) Looping 24 view angles, xp Y+, zm X-, ..., Press Esc to see next view angle.
		s" 查看 24 種視角, Output Area 顯示當前視角, e.g. 'xp Z+ *' 其中 * 表示為 6 種標準視角之一, 按 ESC 倫跳, bye 結束執行。 " msgbox
		\ py> sys.modules['__main__'].gom ( gom )
		py> gom begin
			." xp Y+	  " dup :: script.view.set_xp(up_axis='Y+',use_animation=False,widget='3d_view') <py> ok("") </py> \	 1
			." xp Z+ (X+) " dup :: script.view.set_xp(up_axis='Z+',use_animation=False,widget='3d_view') <py> ok("") </py> \	 2
			." xp Y-	  " dup :: script.view.set_xp(up_axis='Y-',use_animation=False,widget='3d_view') <py> ok("") </py> \	 3
			." xp Z-	  " dup :: script.view.set_xp(up_axis='Z-',use_animation=False,widget='3d_view') <py> ok("") </py> \	 4
			." xm Y+	  " dup :: script.view.set_xm(up_axis='Y+',use_animation=False,widget='3d_view') <py> ok("") </py> \	 5
			." xm Z-	  " dup :: script.view.set_xm(up_axis='Z-',use_animation=False,widget='3d_view') <py> ok("") </py> \	 6
			." xm Y-	  " dup :: script.view.set_xm(up_axis='Y-',use_animation=False,widget='3d_view') <py> ok("") </py> \	 7
			." xm Z+ (X-) " dup :: script.view.set_xm(up_axis='Z+',use_animation=False,widget='3d_view') <py> ok("") </py> \	 8
			." yp X+	  " dup :: script.view.set_yp(up_axis='X+',use_animation=False,widget='3d_view') <py> ok("") </py> \	 9
			." yp Z-	  " dup :: script.view.set_yp(up_axis='Z-',use_animation=False,widget='3d_view') <py> ok("") </py> \ 10
			." yp X-	  " dup :: script.view.set_yp(up_axis='X-',use_animation=False,widget='3d_view') <py> ok("") </py> \ 11
			." yp Z+ (Y+) " dup :: script.view.set_yp(up_axis='Z+',use_animation=False,widget='3d_view') <py> ok("") </py> \ 12
			." ym X+	  " dup :: script.view.set_ym(up_axis='X+',use_animation=False,widget='3d_view') <py> ok("") </py> \ 13
			." ym Z+ (Y-) " dup :: script.view.set_ym(up_axis='Z+',use_animation=False,widget='3d_view') <py> ok("") </py> \ 14
			." ym X-	  " dup :: script.view.set_ym(up_axis='X-',use_animation=False,widget='3d_view') <py> ok("") </py> \ 15
			." ym Z-	  " dup :: script.view.set_ym(up_axis='Z-',use_animation=False,widget='3d_view') <py> ok("") </py> \ 16
			." zp X+	  " dup :: script.view.set_zp(up_axis='X+',use_animation=False,widget='3d_view') <py> ok("") </py> \ 17
			." zp Y+ (Z+) " dup :: script.view.set_zp(up_axis='Y+',use_animation=False,widget='3d_view') <py> ok("") </py> \ 18
			." zp X-	  " dup :: script.view.set_zp(up_axis='X-',use_animation=False,widget='3d_view') <py> ok("") </py> \ 19
			." zp Y-	  " dup :: script.view.set_zp(up_axis='Y-',use_animation=False,widget='3d_view') <py> ok("") </py> \ 20
			." zm X+	  " dup :: script.view.set_zm(up_axis='X+',use_animation=False,widget='3d_view') <py> ok("") </py> \ 21
			." zm Y-	  " dup :: script.view.set_zm(up_axis='Y-',use_animation=False,widget='3d_view') <py> ok("") </py> \ 22
			." zm X-	  " dup :: script.view.set_zm(up_axis='X-',use_animation=False,widget='3d_view') <py> ok("") </py> \ 23
			." zm Y+ (Z-) " dup :: script.view.set_zm(up_axis='Y+',use_animation=False,widget='3d_view') <py> ok("") </py> \ 24
		again ;
	: goto BL word word drop BL word drop ; // ( <label> -- ) Jump to after <label>. 實驗用 skip leading lines of a .f script file.
	: reload-project // ( -- ) Reload the current project file
		<py>
		pathname = gom.app.project.project_file
		gom.script.sys.close_project()
		gom.script.sys.load_project(file=pathname)
		</py> ;
	: reset-project // ( -- ) Delete existing leftings
		part <py>
		part = pop() # 'Part'
		gom.script.cad.delete_element (
			elements=gom.ElementSelection (
				{'category': [
					'key', 'elements',
					'part', gom.app.project.parts[part],
					'explorer_category', 'nominal'
					]},
				{'category': [
					'key', 'elements',
					'part', gom.app.project.parts[part],
					'explorer_category', 'actual'
					]},
				{'category': [
					'key', 'elements',
					'part', gom.app.project.parts[part],
					'explorer_category', 'inspection'
					]},
				{'category': [
					'key', 'elements',
					'part', gom.app.project.parts[part],
					'explorer_category', 'alignment'
					]},
				{'category': [
					'key', 'elements',
					'explorer_category', 'tags'
					]},
				{'category': [
					'key', 'elements',
					# 'is_element_in_clipboard', 'False',
					'explorer_category', 'reports'
					]},
			),
			with_measuring_principle=True
		)
		</py> ;

	: mesh-points // ( -- ElementSelection ) Mesh points created by: CONSTRUCT > point > point
		part <py>
		part = pop() # 'Part'
		points = gom.ElementSelection({
			'category':[
				'key',
				'elements',
				'part',
				gom.app.project.parts[part],
				'explorer_category',
				'actual',
				'object_family',
				'geometrical_element',
				'type',
				'point']
		})
		push(points) </py> ;

	: cad-points // ( -- ElementSelection ) CAD points created by: CONSTRUCT > point > point
		part <py>
		part = pop() # 'Part'
		points = gom.ElementSelection({
			'category':[
			'key', 'elements',
			'part', gom.app.project.parts[part],
			'explorer_category', 'nominal',
			'object_family', 'geometrical_element',
			'type', 'inspection_point'
			]
		})
		push(points) </py> ;

	: surface-points // ( -- ElementSelection ) Surface points created by: CONSTRUCT > point > point
		part <py>
		part = pop() # 'Part'
		points = gom.ElementSelection({
			'category': [
			'key', 'elements',
			'part', gom.app.project.parts[part],
			'explorer_category', 'nominal',
			'object_family', 'geometrical_element',
			'type', 'inspection_surface_point'
			]
		})
		push(points) </py> ;

	: get-view // ( -- view ) Get recent view, an object with 'up direction', 'view direction', 'position' and 'scale'.
		py> gom.app.views.active ;
		\ active 就是眼前看到的，怎麼亂指定 parts[n] 都一樣：
		\ py> gom.app.project.parts['Z-'].actual.views.active py> gom.app.get('views.active') = --> True (<class 'bool'>)
		\ py> gom.app.project.parts['Z+'].actual.views.active py> gom.app.get('views.active') = --> True (<class 'bool'>)
		\ py> gom.app.project.parts[0].actual.views.active py> gom.app.get('views.active') = --> True (<class 'bool'>)
		\ py> gom.app.project.parts[1].actual.views.active py> gom.app.get('views.active') = --> True (<class 'bool'>)

	: set-view // ( view -- ) Set active view
		<py>
			gom.script.view.set_view_cartesian(
				camera_position=tos().position,
				view_direction=tos().view_direction,
				up_direction=tos().up_direction,
				scale=tos().scale,
				use_animation=False,
				widget='3d_view')
		</py> drop ;

	: report-init // ( -- ) Initialize report to start from page 1
		<py>
		gom.script.report.set_template_orientation (
			orientation='portrait',
			report_templates=[gom.app.project.report_templates['Style_a4'].template['3D+3D']])
		</py> ;

	: make-report // ( -- ) Make a A4 3D+3D portrait report at the recent view angle
		<py>
		gom.script.report.create_report_page (
			animated_page=False,
			imitate_fit_mode='overwrite',
			master_name='Style_a4',
			template_name='3D+3D',
			template_orientation='portrait',
			template_package={'name': 'Inspection', 'uuid': 'a6769fbc-4bda-4cec-af9a-b189baf8b742', 'version': '1.0.0'},
			title='Untitled')
		</py> ;

	: dict>view // ( dict -- view ) Convert a view dict (from user) into the view object
		get-view ( dictView view )
		py: tos().position=gom.Vec3d(**tos(1)['position'])
		py: tos().scale=tos(1)['scale']
		py: tos().up_direction=gom.Vec3d(**tos(1)['up_direction'])
		py: tos().view_direction=gom.Vec3d(**tos(1)['view_direction'])
		nip ;

	: standard-view // ( "ypZ+" -- ) Turn standard view to one of the 24 view angles
		<py>
			table = {
				"xpY+": lambda: gom.script.view.set_xp(up_axis='Y+',use_animation=False,widget='3d_view'),
				"xpZ+": lambda: gom.script.view.set_xp(up_axis='Z+',use_animation=False,widget='3d_view'),
				"xpY-": lambda: gom.script.view.set_xp(up_axis='Y-',use_animation=False,widget='3d_view'),
				"xpZ-": lambda: gom.script.view.set_xp(up_axis='Z-',use_animation=False,widget='3d_view'),
				"xmY+": lambda: gom.script.view.set_xm(up_axis='Y+',use_animation=False,widget='3d_view'),
				"xmZ-": lambda: gom.script.view.set_xm(up_axis='Z-',use_animation=False,widget='3d_view'),
				"xmY-": lambda: gom.script.view.set_xm(up_axis='Y-',use_animation=False,widget='3d_view'),
				"xmZ+": lambda: gom.script.view.set_xm(up_axis='Z+',use_animation=False,widget='3d_view'),
				"ypX+": lambda: gom.script.view.set_yp(up_axis='X+',use_animation=False,widget='3d_view'),
				"ypZ-": lambda: gom.script.view.set_yp(up_axis='Z-',use_animation=False,widget='3d_view'),
				"ypX-": lambda: gom.script.view.set_yp(up_axis='X-',use_animation=False,widget='3d_view'),
				"ypZ+": lambda: gom.script.view.set_yp(up_axis='Z+',use_animation=False,widget='3d_view'),
				"ymX+": lambda: gom.script.view.set_ym(up_axis='X+',use_animation=False,widget='3d_view'),
				"ymZ+": lambda: gom.script.view.set_ym(up_axis='Z+',use_animation=False,widget='3d_view'),
				"ymX-": lambda: gom.script.view.set_ym(up_axis='X-',use_animation=False,widget='3d_view'),
				"ymZ-": lambda: gom.script.view.set_ym(up_axis='Z-',use_animation=False,widget='3d_view'),
				"zpX+": lambda: gom.script.view.set_zp(up_axis='X+',use_animation=False,widget='3d_view'),
				"zpY+": lambda: gom.script.view.set_zp(up_axis='Y+',use_animation=False,widget='3d_view'),
				"zpX-": lambda: gom.script.view.set_zp(up_axis='X-',use_animation=False,widget='3d_view'),
				"zpY-": lambda: gom.script.view.set_zp(up_axis='Y-',use_animation=False,widget='3d_view'),
				"zmX+": lambda: gom.script.view.set_zm(up_axis='X+',use_animation=False,widget='3d_view'),
				"zmY-": lambda: gom.script.view.set_zm(up_axis='Y-',use_animation=False,widget='3d_view'),
				"zmX-": lambda: gom.script.view.set_zm(up_axis='X-',use_animation=False,widget='3d_view'),
				"zmY+": lambda: gom.script.view.set_zm(up_axis='Y+',use_animation=False,widget='3d_view'),
			}
			table[pop()]()
		</py> ;
		/// Usage: char ypZ+ standard-view

	: adjust-view // ( point -- ) adjust_view_to_element_by_front_view 以指定點為中心的視角
		<py>
		gom.script.view.adjust_view_to_element_by_front_view (
			element=pop(),
			use_animation=False
		)
		</py> ;

	: rotate // ( CenterPoint axis 180 -- ) Rotate for the 2nd frame of a report given the Camera Position as the center point.
		<py>
		gom.script.view.rotate_3d_view (
			rotation_angle=pop(), # 180
			rotation_axis='cube_?'.replace("?",pop()),	# axis
			rotation_center=pop(),
			use_animation=False,  # 跑 Script 時，若用 True 可能會干擾到後續的動作。
			widget='3d_view')
		</py> ;
		/// Where axis comes form:
		///		setup :> parameter['core_side'][0] ( "y" ) \ 取得旋轉軸心, core side 的法線方向。

	: upsidedown // ( n -- ) Turn upside down the 2nd frame of the report# n (int)
		<py>
		gom.script.sys.switch_to_report_workspace()
		gom.script.report.overwrite_report_page (target=[gom.app.project.reports[pop()].pages[0].elements[0]])
		gom.script.sys.switch_to_inspection_workspace()
		</py> ;

	: sorted-xyz // ( -- ['x','z','y'] ) Sorted xyz of bounding box bigest to smallest
		part <py>
		part = pop() # 'Part'
		bb = gom.app.project.parts[part].nominal.bounding_box	 # bounding box
		dim = bb.max - bb.min
		dim = {'x':dim.x, 'y':dim.y, 'z':dim.z}
		xyz = sorted(dim, key=dim.get, reverse=True)  # xyz is a sorted list like ['x', 'z', 'y'] where [0] is the biggest
		push(xyz)
		</py> ;
		/// 用來看出 project 的軸向，最小的就是 core side, cavity side, 中間的就是朝上、朝下。

	: bl // ( -- ) List all breakpoints
		__main__ :> peforth.bps 
		<py>
		bps = pop()
		print('Disabled breakpoints:')
		for i in range(len(bps)):
			if not bps[i]: 
				print(i, end=' ')
		print(); print('Enabled breakpoints:')
		count = 0
		for i in range(len(bps)):
			if bps[i]: 
				print(i, end=' ')
				count += 1
		print(); print('Enabled breakpoints count: {}/{}'.format(count,len(bps)))
		</py> cr ;
		/// Breakpoint commands:
		///	  bl  - list all breakpoints (capital BL is white space) 
		///	  be  - enable breakpoints, e.g. be 1 2 3 
		///	  bd  - disable breakpoints, e.g. bd 1 2 3 
		///	  be* - enable all breakpoints
		///	  bd* - disable all breakpoints 
		/// Also: 
		///   for i in [11,22,33]: peforth.bps[i]=0	 # disable breakpoints 11,22,33 
		///   for i in [11,22,33]: peforth.bps[i]=i	 # enable  breakpoints 11,22,33 

	: bd // ( <1 2 3 4...> -- ) Disable listed breakpoints 
		CR word ( line ) __main__ :> peforth.bps ( line bps )
		<py>
		line, bps = pop(1), pop(0)
		points = map(int, line.split(' '))
		for i in points: bps[i] = 0
		</py> ; 
		' bl :> comment last :: comment=pop(1)

	: be // ( <1 2 3 4...> -- ) Enable listed breakpoints 
		CR word ( line ) __main__ :> peforth.bps ( line bps ) 
		<py>
		line, bps = pop(1), pop(0)
		points = map(int, line.split(' '))
		for i in points: bps[i] = i
		</py> ; 
		' bl :> comment last :: comment=pop(1)

	: bd* // ( -- ) Disable all breakpoints 
		__main__ :> peforth.bps	 ( bps ) 
		<py>
		bps = pop()
		for i in range(len(bps)): bps[i] = 0
		</py> ;
		' bl :> comment last :: comment=pop(1)

	: be* // ( -- ) Enable all breakpoints 
		__main__ :> peforth.bps	 ( bps ) 
		<py>
		bps = pop()
		for i in range(len(bps)): bps[i] = i
		</py> ;
		' bl :> comment last :: comment=pop(1)
		
	""")

if __name__ == '__main__':
	peforth.bp(11,locals())
	peforth.bp(22,locals())	
