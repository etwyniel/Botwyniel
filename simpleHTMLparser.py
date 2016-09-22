def get_text(html, blacklist=['script', 'style', 'blockquote', 'p', 'em', 'br', '/em']):
	r = ""
	current_tag = ""
	is_text = False
	is_tag = False
	for c in html:
		if c == '<':
			is_tag = True
			current_tag = ""
			is_text = False
		elif c == '>':
			is_tag = False
			if current_tag in blacklist:
				is_text = False
			else:
				is_text = True
				if current_tag == '/span':
					r += ' '
				#r += '\n'
		elif is_tag:
			if c == ' ':
				is_tag = False
			else:
				current_tag += c
		elif is_text:
			r += c
	return r