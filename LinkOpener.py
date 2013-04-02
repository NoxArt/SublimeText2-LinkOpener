# Copyright (c) 2012 Jiri "NoxArt" Petruzelka
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

import sublime
import sublime_plugin
import webbrowser
import re
import urllib2

junk = r"(?:\s|\;|\)|\]|\[|\{|\}|,|\"|'|:|\<|$|\.\s)"
head = r"(?:(?:(?:http|https|ftp)://(?:\S+?))|(?:\bwww\.\S+?))"

regexFindUrl = "(" + head + ")" + junk
findUrl = re.compile(regexFindUrl, re.I)
findUrlExact = re.compile("^" + regexFindUrl + "$", re.I)
findJunk = re.compile(junk + "$", re.I)

settings = sublime.load_settings('linkopener.sublime-settings')


def isLink(text):
    return text[:7] is "http://" or text[:7] is "http://"


def findLinks(text):
    return re.findall(findUrl, text)


def isSelectionLink(text):
    return findUrlExact.match(text) is not None


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


class SelectNextUrlCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        selection = self.view.sel()
        finalSelection = None
        index = -1

        for select in selection:
            contents = self.view.substr(select)

            if select.begin() == select.end():
                select = sublime.Region(select.begin(), self.view.size())
            elif len(contents) > 0 and isSelectionLink(contents):
                select = sublime.Region(select.end(), self.view.size())

            contents = self.view.substr(select)
            link = findLinks(contents)
            index += 1

            if len(link) > 0:
                finalSelection = select
                break

        if len(selection) is 0 or len(link) is 0:
            select = sublime.Region(0, self.view.size())
            contents = self.view.substr(select)
            link = findLinks(contents)

            if len(link) > 0:
                finalSelection = select

        if len(link) > 0:
            if type(link[0]) is tuple:
                link[0] = link[0][0]

            result = self.view.find(link[0], finalSelection.begin(), sublime.LITERAL)

            region = sublime.Region(result.begin(), result.end())

            selection.clear()
            selection.add(region)


class SelectAllUrlsCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        selection = self.view.sel()

        select = sublime.Region(0, self.view.size())
        contents = self.view.substr(select)
        link = findLinks(contents)

        if len(link) > 0:
            link = map(re.escape, link)
            links = "|".join(link)

            result = self.view.find_all(links)
            selection.clear()

            for reg in result:
                region = sublime.Region(reg.begin(), reg.end())
                selection.add(region)

class SearchTermCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        selection = self.view.sel()
        select = sublime.Region(0, self.view.size())

        selection = self.view.sel()
        terms = []

        for select in selection:
            contents = self.view.substr(select)
            if contents not in terms:
                terms.append(urllib2.quote(contents.encode("utf8")))


        for term in terms:
            link = settings.get('search_url').replace('%s', term)

            webbrowser.open(link, 1, True)

