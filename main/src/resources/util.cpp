#include <iostream>
#include <string>
#include <vector>
#include <set>

using namespace std;

void split(const string& str, vector<string>& tokens, const string& delimiters = " ")
{
    // Skip delimiters at beginning.
    string::size_type lastPos = str.find_first_not_of(delimiters, 0);
    // Find first "non-delimiter".
    string::size_type pos     = str.find_first_of(delimiters, lastPos);

    while (string::npos != pos || string::npos != lastPos)
    {
        // Found a token, add it to the vector.
        tokens.push_back(str.substr(lastPos, pos - lastPos));
        // Skip delimiters.  Note the "not_of"
        lastPos = str.find_first_not_of(delimiters, pos);
        // Find next "non-delimiter"
        pos = str.find_first_of(delimiters, lastPos);
    }
}

vector<string> tokenize(string text) {
    vector<string> lines;
    split(text, lines, "\n");

    for (int i = 0; i < lines.size(); i++) {
        if (lines[i].find_first_of("///") != string::npos)
            cout << lines[i].find_first_of("///") << endl;
    }

    return lines;
}

int main(int argc, char **argv)
{
    vector<string> result;
    result = tokenize("123\n456\n789");
}
