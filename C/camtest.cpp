#include <iostream>
#include "cv.h"
#include "highgui.h"

using namespace std;
using namespace cv;

int main() {
	Mat image;

	image = imread("", 1);

	if(!image.data) {
		printf("No Image Data\n");

		return -1;
	}

	namedWindow("Display Image", CV_WINDOW_AUTOSIZE);
	imshow("Display Image", image);

	waitKey(0);

	return 0;
}