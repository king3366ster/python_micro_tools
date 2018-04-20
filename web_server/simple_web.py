import web

urls = (
    '/', 'index',
    '/t', 'test'
)

render = web.template.render('templates/')

class index:
    def GET(self):
        # return "Hello, world!"
        return render.index()

class test:
    def GET(self):
        # return "Hello, world!"
        return render.test()
    def POST(self):
        ct = web.ctx.env.get('CONTENT_TYPE')
        print web.ctx.env
        return ct

if __name__ == "__main__":
    # python simple_web.py 1234
    app = web.application(urls, globals())
    app.run()
