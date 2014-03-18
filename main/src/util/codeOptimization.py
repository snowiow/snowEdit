import threading
import re
import copy

import RaschLexer

wordDelimiterList = ['.', ',', '[', '(', ' ', '\n', ';', ':', '{', '>', '<',
                     ')', '}', ']']


class Optimizer():
    def __init__(self):
        pass

    def optimize(self, text, isJava, noteFlag, progressBar):
        variables = self.getVariableUsageMap(text)

        line = 1
        suggestions = ''
        i = 0
        if len(text) - 1 < 2:
            progressBar.setMaximum = 2
        else:
            progressBar.setMaximum(len(text) - 1)
        while i < len(text):
            progressBar.setValue(i)
            if text[i] == '\n':
                i += 1
                line += 1
                continue

            if text[i] == '/':
                i += 1
                if text[i] == '/':
                    i += 1
                    while text[i] != '\n' and i < len(text) - 1:
                        i += 1
                    continue
                elif text[i] == '*':
                    while text[i] != '*' and text[i + 1] != '/' and i < len(
                            text) - 1:
                        i += 2
                    continue

            if noteFlag:
                if text[i] == '.':
                    i += 1
                    if text[i] == '.':
                        i += 1
                        while text[i] == ' ':
                            i += 1
                        if text[i].isdigit():
                            suggestions += 'Slice at line {} isn\'t ' \
                                           'allowed if -no_tc flag is ' \
                                           'activated.\n\n'.format(line)

            if text[i] == 'c':
                i += 1
                if text[i] == 'o':
                    i += 1
                    if text[i] == 'n':
                        i += 1
                        if text[i] == 's':
                            i += 1
                            if text[i] == 't':
                                suggestions += 'Think about using alias ' \
                                               'instead ' \
                                               'of const, at line {}, if you ' \
                                               'want ' \
                                               'to have the variable ' \
                                               'calculated at' \
                                               ' compiletime instead of at ' \
                                               'runtime.\n\n'.format(line)

            if text[i] == '=' or text[i] == '(' or text[i] == '[' \
                    or text[i] == ':':
                i += 1
                self.lookForVariablesUsed(text, i, variables)

            if text[i] == '-' and text[i + 1] == '>':
                i += 2
                self.lookForVariablesUsed(text, i, variables)
                if isJava:
                    suggestions += 'Pointer at line {} isn\'t allowed, ' \
                                   'if you want to compile to java code.\n\n' \
                        .format(line)

            i += 1

        for var in variables:
            if variables[var] >= 0:
                suggestions += var + ' is an unused variable at line {}.\n\n' \
                    .format(variables[var]) \
                    .format(line)
        print suggestions
        return suggestions

    def getVariableUsageMap(self, text):
        textArray = text.split('\n')
        results = {}
        for line in range(len(textArray)):
            items = RaschLexer.getVariables(textArray[line])
            for item in items:
                results.update({item: line + 1})
        return results

    def lookForVariablesUsed(self, text, i, variables):
        j = copy.copy(i)
        results = []
        startChar = -1
        endChar = -1
        while j < len(text):
            if text[j] == '$' or text[j] == '@':
                startChar = j
            if text[j] in wordDelimiterList:
                endChar = j
                if endChar > startChar and startChar >= 0 and endChar >= 0:
                    results.append(text[startChar:endChar])
                    startChar = -1
                    endChar = -1
            if text[j] == '\n' or text[j] == ';':
                break
            j += 1
        for var in results:
            if var in variables:
                variables[var] = -1

