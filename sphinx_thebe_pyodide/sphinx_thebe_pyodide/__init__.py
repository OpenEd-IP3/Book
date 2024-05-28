from sphinx.application import Sphinx

def setup(app: Sphinx):
    app.add_js_file('https://cdn.jsdelivr.net/pyodide/v0.18.1/full/pyodide.js')
    app.add_js_file('sphinx_thebe_pyodide/static/custom.js')
    return {
        'version': '0.1',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }

