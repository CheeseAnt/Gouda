#include <iostream>
#include <string>
#include <Windows.h>
#include <stdio.h>

/* Little program to lowercase all files in current directory
* By Anton Shmatov 23/8/2017 */


using namespace std;

char* convertToLower(char*);

bool changed = false;

int main() {
	WIN32_FIND_DATA fd;
	HANDLE hFind = ::FindFirstFile("*.*", &fd);

	if(hFind != INVALID_HANDLE_VALUE) {
		do {
			if(! (fd.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY)) {
				char* fn = (char*) fd.cFileName;

				char* fnNew = convertToLower(fn);

				if(changed)
					rename(fn, fnNew);
			}
		}
		while(::FindNextFile(hFind, &fd));

		::FindClose(hFind);
	}

	cout << endl << "Completed; Press Enter to exit." << endl;

	cin.get();

	return 0;
}

char* convertToLower(char* filename) {
	changed = false;

	for(unsigned int i = 0; i <= strlen(filename); i++) {
		if(filename[i] >= 'A' && filename[i] <= 'Z') {
			filename[i] += 'a' - 'A';

			changed = true;
		}
	}

	if(changed)
		cout << "Converted file: " << filename << endl;

	return filename;
}