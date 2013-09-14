from pythonHighlighter import PythonHighlighter
from raschHighlighter import RaschHighlighter
from NoneHighlighter import NoneHighlighter


def chooseHighlighter(editor, filePath):
    if filePath.find('.') > -1:
        if filePath.rsplit('.', 1)[1] == 'py':
            return PythonHighlighter(editor)
        elif filePath.rsplit('.', 1)[1] == 'rs':
            return RaschHighlighter(editor)
        return NoneHighlighter(editor)
    return NoneHighlighter(editor)
