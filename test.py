import codegen, jinja2, spidermonkey, sys
import simplejson as json

TESTS = [
	('{{ test }}', {'test': 'crap'}),
	('{% if a %}x{% endif %}', {'a': True}),
	('{% if a %}c{% endif %}b', {'a': False}),
	('{{ 1 if a else 2 }}', {'a': True}),
	('{{ 1 if a else 2 }}', {'a': False}),
	('{% if a %}d{% else %}e{% endif %}', {'a': False}),
	('{% if a %}f{% elif b %}g{% endif %}', {'b': True}),
	("{{ '%4.2f'|format(x) }}", {'x': 17.0}),
	('{{ d[:7] }}', {'d': '2011-05-27'}),
	('{{ a.x }}', {'a': {'x': 'z'}}),
	('{{ "%.6f"|format(a / b) }}', {'a': 5.0, 'b': 3}),
	('{{ "%.1f"|format(a.x / b.y * 100) }}', {'a': {'x': 20}, 'b': {'y': 5}}),
	('{% macro x(y) %}{{ y / 2 }}{% endmacro %}{{ x(z) }}', {'z': 512}),
	(
		'{% macro x(y, z) %}{{ y + z }}{% endmacro %}{{ x(y, z) }}',
		{'z': 512, 'y': 3},
	),
	('{{ x is none }}', {'x': None}),
	('{{ "%.2f%%"|format(a) }}', {'a': 5}),
]

def loader(i):
	return jinja2.DictLoader({'index': TESTS[i][0]})

def jstest(env, data):
	run = spidermonkey.Runtime()
	ctx = run.new_context()
	js = codegen.generate(env)
	jsobj = json.dumps(data)
	code = js + '\ntemplates.index.render(%s);' % jsobj
	return ctx.execute(code)

def pytest(env, data):
	tmpl = env.get_template('index')
	return tmpl.render(data)

def run(i, quiet=True):
	
	src, data = TESTS[i]
	env = jinja2.Environment(loader=loader(i))
	ast = codegen.compile(env, src)
	
	if not quiet:
		print ast
		print codegen.generate(env)
	
	js = jstest(env, data)
	py = pytest(env, data)
	
	if not quiet:
		print 'js:', repr(js)
		print 'py:', repr(py)
	
	if isinstance(js, str) and js.isdigit():
		return float(js) == float(py)
	if {'true': 'True', 'false': 'False'}.get(js, js) == py:
		return True
	return js == py

def test():
	for i, t in enumerate(TESTS):
		res = run(i)
		sys.stdout.write('.' if res else 'F')
	sys.stdout.write('\n')

if __name__ == '__main__':
	args = sys.argv[1:]
	if args:
		run(int(args[0]), False)
	else:
		test()
