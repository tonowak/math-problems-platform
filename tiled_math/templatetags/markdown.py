from django import template
from markdown import markdown

register = template.Library()

@register.tag(name="markdown")
def markdown_tag(parser, token):
    nodelist = parser.parse(('endmarkdown',))
    parser.delete_first_token()
    return MarkdownNode(nodelist)

class MarkdownNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist
    
    def render(self, context):
        output = self.nodelist.render(context)
        output = output.replace('\\', '\\\\')
        output = markdown(output)
        output = '<span class="markdown">' + output + '</span>'
        return output
