from pythonHighlighter import PythonHighlighter
from raschHighlighter import RaschHighlighter
from noneHighlighter import NoneHighlighter
from cppHighlighter import CppHighlighter


def chooseHighlighter(editor, filePath):
    if filePath.find('.') > -1:
        fileEnding = filePath.rsplit('.', 1)[1]
        if fileEnding == 'py':
            return PythonHighlighter(editor)
        elif fileEnding == 'rs':
            return RaschHighlighter(editor)
        elif fileEnding == 'cpp' or fileEnding == 'h':
            return CppHighlighter(editor)
        return NoneHighlighter(editor)
    return NoneHighlighter(editor)
