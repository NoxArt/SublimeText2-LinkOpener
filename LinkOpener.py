import sublime
import sublime_plugin
import webbrowser
import re

junk = r"(?:\s|\;|\)|\]|\[|\{|\}|,|\"|'|:|\<|$|\.\s)"
head = r"(?:(?:(?:http|https|ftp)://(?:\S*?\.\S+?))|(?:\bwww\.\S+?))"
findUrl = re.compile("(" + head + junk + ")", re.I)
findJunk = re.compile(junk + "$", re.I)

settings = sublime.load_settings('linkopener.sublime-settings')


def isLink(text):
    return text[:7] is "http://" or text[:7] is "http://"


def findLinks(text):
    return re.findall(findUrl, text)


def cleanLink(link):
    return re.sub(findJunk, '', link)


def fixLink(link):
    if link[:4] is "www.":
        link = "http://" + link

    return link


def statusInfo(opened):
    if len(opened) > 0:
        message = "Opening link"
        if len(opened) > 1:
            message += "s"

        message += ": "

        for link in opened:
            message += " [" + link + "]"

    else:
        message = "No link found"

    return "LinkOpener > " + message


class OpenUrlCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        selection = self.view.sel()
        links = []

        for select in selection:
            contents = self.view.substr(select)
            links += findLinks(contents)

        opened = []
        for link in links:
            link = cleanLink(link)
            link = fixLink(link)

            if link is not None and link not in opened:
                webbrowser.open(link, 1, settings.get('raise_window'))
                opened.append(link)

            if settings.get('first_link_only'):
                break

        sublime.status_message(statusInfo(opened))
