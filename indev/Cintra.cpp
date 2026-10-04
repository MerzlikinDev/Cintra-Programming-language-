#include <iostream>
#include <fstream>
#include <vector>
#include <utility>
#include <string>

using namespace std;


vector<string> split(const string& line) {
    vector<string> res;

    {
        ofstream out("CintraSystem.cnt");
        out << line;
    }

    ifstream in("CintraSystem.cnt");
    string word;
    while (in >> word) {
        res.push_back(word);
    }
    return res;
}
int run_code(string file_name){
    vector<pair<string, string>> stack{};
    ifstream file(file_name);
    string line;
    while (getline(file, line)) {
        vector<string> splited_line = split(line);
        if (splited_line[0] == "out") {
            size_t i = 1;
            try {
                while (true) {
                    cout << splited_line.at(i) << " ";
                    i++;
                }
            }catch(exception& e) {
                cout << "\n";
                break;
            }
            
        }
        else if (splited_line[0] == "in") {
            cin >> splited_line[1];
            
        }
        else {
            string name = splited_line[1],  value = splited_line[3];
            for (auto i : stack) {
                if (i.first == name)
                    i.second = value;
                    for (auto i : stack)
                        cout << i.first << " " << i.second << endl;

            }

            return 0;
        }
    }
    file.close();
    cout << "Program have been done with exit code 0.";
    return 0;
}

int main() {
    string a;
    cout << "Enter file name: ";
    getline(cin, a);
    run_code(a);
    return 0;
}
