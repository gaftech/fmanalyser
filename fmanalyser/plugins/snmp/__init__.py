import os.path

FMANALYSER_MIB_NAME = 'FMANALYSER-MIB'

PLUGIN_DIR = os.path.abspath(os.path.dirname(__file__))
MIB_DIR = os.path.join(PLUGIN_DIR, 'mibs')
TEMPLATE_DIR = os.path.join(PLUGIN_DIR, 'templates')
DEFAULT_MIB_FILE = os.path.join(MIB_DIR, FMANALYSER_MIB_NAME)
DEFAULT_PYMIB_FILE = os.path.join(MIB_DIR, '%s.py' % FMANALYSER_MIB_NAME)

ROOT_TEMPLATE = os.path.join(TEMPLATE_DIR, '%s.tmpl' % FMANALYSER_MIB_NAME)
VARIABLE_TEMPLATE = os.path.join(TEMPLATE_DIR, 'ChannelVariable.tmpl')
OPTION_TEMPLATE = os.path.join(TEMPLATE_DIR, 'VariableOption.tmpl')


def render_template(filename, **context):
    with open(filename) as fp:
        template = fp.read()
    return template % context