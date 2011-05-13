import codegen, jinja2, spidermonkey, sys
import simplejson as json

def jstest(env, src, data):
	run = spidermonkey.Runtime()
	ctx = run.new_context()
	js = codegen.generate(env, codegen.compile(env, src))
	jsobj = json.dumps(data)
	code = js + '\ntemplate.render(%s);' % jsobj
	return ctx.execute(code)

def pytest(env, src, data):
	tmpl = env.from_string(src)
	return tmpl.render(data)

WORKS = [
	('{{ test }}', {'test': 'crap'}),
	('{% if a %}x{% endif %}', {'a': True}),
]

# next:
# - if/elif/else/endif
# - assignment + cond-expr
# - for-loop
# - object access
# - filters

src, data = WORKS[int(sys.argv[1])]
env = jinja2.Environment()
ast = codegen.compile(env, src)
print ast
print codegen.generate(env, ast)

print 'js:', repr(jstest(env, src, data))
print 'py:', repr(pytest(env, src, data))
