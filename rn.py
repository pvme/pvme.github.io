from formatter.discord_markdown import DiscordMarkdownExtension
import markdown

MD = markdown.Markdown(extensions=[DiscordMarkdownExtension()])


text = "__underline__ **bold** *italic* ~~strikethrough~~ `code` ```codeblock```"
print(MD.convert(text))