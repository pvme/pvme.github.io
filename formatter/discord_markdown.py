from markdown.inlinepatterns import SimpleTagInlineProcessor
from markdown.extensions import Extension


class DiscordMarkdownExtension(Extension):
    def extendMarkdown(self, md):
        md.inlinePatterns.register(SimpleTagInlineProcessor(r'()__(.*?)__', 'u'), 'underscore', 175)
        md.inlinePatterns.register(SimpleTagInlineProcessor(r'()~~(.*?)~~', 'del'), 'del', 174)
