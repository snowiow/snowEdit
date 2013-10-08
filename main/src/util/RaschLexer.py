#-*- coding: utf-8 -*-


class RaschLexer():
    """
    RaschLexer is a class, which is needed for the autocompletion in snowedit.
    The RaschLexer tokenizes the text within the editor and filters the
    important informations
    """

    def __init__(self):

        #seperators, by which the text gets separated
        self._opList = [' ', ',', '.', '=', '+', '-', ';', '(', ')', '[',
                        ']']

    def _tokenize(self, text):
        """
        _tokenize deletes all kinds of comments. Then it splits the text by
        the separators from the opList into tokens
        """
        l = text.split('\n')
        toBeDeleted = set([])
        deleteLine = False

        for i in range(len(l) - 1):

            if deleteLine:
                toBeDeleted.update([i])

            if l[i].find('///') != -1:
                current = (l[i].split('///')[0])
                # special case: int = 1 /* test */; /// hi
                if current.find('/*'):
                    l.append(current.split('/*')[0])
                else:
                    l.append(current)
                toBeDeleted.update([i])

            if l[i].find('/*') != -1:
                deleteLine = True
                l.append(l[i].split('/*')[0])
                toBeDeleted.update([i])

            if l[i].find('*/') != -1:
                l.append(l[i].split('*/')[1])
                toBeDeleted.update([i])
                deleteLine = False

        #set is unsorted and because to not fuck up the list. entries get
        # deleted in reverse order
        for i in reversed(sorted(toBeDeleted)):
            del l[i]

        s = set(l)
        for op in self._opList:
            temp = set([])
            for entry in s:
                temp.update(entry.split(op))

            s = temp

        return s

    def getVariables(self, text):
        """
        GetVariables gets the tokens from the _tokenize function and returns
        every occurrence with $ or @.
        """
        array = self._tokenize(text)
        result = set([])
        for entry in array:
            if entry.startswith('$') or entry.startswith('@'):
                if len(entry) > 1:
                    result.update([entry])
        return result









