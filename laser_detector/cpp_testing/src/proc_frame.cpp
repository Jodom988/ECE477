#include <stdio.h>
#include <stdint.h>
#include <sys/time.h>
#include <opencv2/opencv.hpp>
#include <opencv2/core/types.hpp>
#include <list>

#define THRESH 50

using namespace cv;
using namespace std;

long current_time_millis();
Point test_detect_in_frame(Mat img, Mat base);
Point detect_in_frame(Mat img, Mat base);
void print_point(Point p);
uchar* get_pixel(Mat img, int x, int y);
void printlist(std::list<Point3d> list);
void add_lines(Mat img, int row, int col, int w);

int main(int argc, char** argv)
{
	// Test video
	if (1)
	{
		VideoCapture cap("./ir-laser-test-1mw-24ma-2.mjpeg");
		//VideoCapture cap(0);

		int fourcc = VideoWriter::fourcc('X','V','I','D');
		int width = 640;
		int height = 480;
		VideoWriter out("./outcpp.mp4", cv::VideoWriter::fourcc('H','2','6','4'), 30, Size(640,480));

		FILE* times_fptr = fopen("../scripts/data/times_proc_frame.txt", "w");

		int i = 0;
		Mat frame;
		Mat base_frame;
		while(1)
		{			
			cap.read(frame);
			printf("Here\n");
			if(frame.empty())
			{
				break;
			}
			printf("Here\n");
			if(i == 0)
			{
				base_frame = Mat(frame);
			}

			out.write(frame);

			Point pos = detect_in_frame(frame, base_frame);

			i++;
		}


		fclose(times_fptr);
	}

	// Test single frame
	if (0)
	{
		Mat image, base;
		base = cv::imread("../imgs/base.jpg", 1);
		image = cv::imread("../imgs/ir-laser-1mw-24ma.jpg", 1);

		uint16_t rows = image.size().height;
		uint16_t cols = image.size().width;

		test_detect_in_frame(image, base);
	}

	return 0;
}

long current_time_millis(){
	struct timeval tp;
	gettimeofday(&tp, NULL);
	return (long) tp.tv_sec * 1000 + tp.tv_usec / 1000;
}

void print_point(Point p){
	printf("(%d, %d)", p.x, p.y);
}

Point detect_in_frame(Mat img, Mat base){
	uint16_t height = img.size().height;
	uint16_t width = img.size().width;

	int N = 4;

	std::list<cv::Point3d> largest_vals;
	largest_vals.push_front(cv::Point3d(0, 0, THRESH));
	
	int max_col = 0;
	for (int row_idx = 0; row_idx < height; row_idx++)
	{
		for (int col_idx = 0; col_idx < width; col_idx++)
		{
			// Calculate diff
			int val = get_pixel(img, col_idx, row_idx)[1] - get_pixel(base, col_idx, row_idx)[1];
			//Add to list
			if (val > largest_vals.back().z)
			{
				for (std::list<Point3d>::iterator it = largest_vals.begin(); it != largest_vals.end(); it++){
					if (val > (*it).z)
					{
						largest_vals.insert(it, Point3d(col_idx, row_idx, val));
						if (largest_vals.size() > N)
						{
							largest_vals.pop_back();
						}
						break;
					}
				}
			}

		}
	}

	if (largest_vals.back().z == THRESH){
		largest_vals.pop_back();
	}

	Point3d sum;
	
	for (std::list<Point3d>::iterator it = largest_vals.begin(); it != largest_vals.end(); it++){
		sum += *it;
	}

	int row_avg = sum.y / N;
	int col_avg = sum.x / N;

	return Point(col_avg, row_avg);
}

Point test_detect_in_frame(Mat img, Mat base){
	uint16_t height = img.size().height;
	uint16_t width = img.size().width;

	Mat new_img(height, width*3, CV_8UC(3));

	int N = 4;

	std::list<cv::Point3d> largest_vals;
	largest_vals.push_front(cv::Point3d(0, 0, THRESH));

	if (height != base.size().height || width != base.size().width){
		printf("Image and Base Image dimensions do not match");
		throw;
	}

	long start = current_time_millis();
	
	int max_col = 0;
	for (int row_idx = 0; row_idx < height; row_idx++)
	{
		for (int col_idx = 0; col_idx < width; col_idx++)
		{
			//Create new image
			for (int i = 0; i < 3; ++i)
			{

				int val = get_pixel(img, col_idx, row_idx)[i] - get_pixel(base, col_idx, row_idx)[i];

				if (val < 0)
					val = 0;
				else if (val > 255)
					val = 255;

				get_pixel(new_img, col_idx+(width*0), row_idx)[i] = get_pixel(base, col_idx, row_idx)[i];
				get_pixel(new_img, col_idx+(width*1), row_idx)[i] = get_pixel(img, col_idx, row_idx)[i];
				get_pixel(new_img, col_idx+(width*2), row_idx)[i] = val;
			}

			int val = get_pixel(img, col_idx, row_idx)[1] - get_pixel(base, col_idx, row_idx)[1];
			//Add to list
			if (val > largest_vals.back().z)
			{
				for (std::list<Point3d>::iterator it = largest_vals.begin(); it != largest_vals.end(); it++){
					if (val > (*it).z)
					{
						largest_vals.insert(it, Point3d(col_idx, row_idx, val));
						if (largest_vals.size() > N)
						{
							largest_vals.pop_back();
						}
						break;
					}
				}
			}

		}
	}

	if (largest_vals.back().z == THRESH){
		largest_vals.pop_back();
	}

	Point3d sum;
	
	for (std::list<Point3d>::iterator it = largest_vals.begin(); it != largest_vals.end(); it++){
		sum += *it;
	}

	int row_avg = sum.y / N;
	int col_avg = sum.x / N;

	printf("Elapsed Time: %ld\n", current_time_millis() - start);

	add_lines(img, row_avg, col_avg, 4);

	namedWindow("Display Image", cv::WINDOW_AUTOSIZE);
	imshow("Display Image", img);

	vector<int> compression_params;
    compression_params.push_back(IMWRITE_PNG_COMPRESSION);
    compression_params.push_back(9);

    imwrite("../imgs/ir-laser-1mw-24ma-detected-cpp.png", img, compression_params);

	waitKey(0);

	return Point(col_avg, row_avg);
}

void add_lines(Mat img, int row, int col, int w)
{
	int width = img.size().width;
	int height = img.size().height;

	cv::line(img, Point(0, row+w), Point(width, row+w), {0, 255, 0});
	cv::line(img, Point(0, row-w), Point(width, row-w), {0, 255, 0});

	cv::line(img, Point(col-w, 0), Point(col-w, height), {0, 255, 0});
	cv::line(img, Point(col+w, 0), Point(col+w, height), {0, 255, 0});
}

uchar* get_pixel(Mat img, int x, int y){
	return (& img.at<uchar>(y, x, 0));
}

void printlist(std::list<Point3d> list)
{
	for(std::list<Point3d>::iterator it = list.begin(); it != list.end(); it++)
	{
		printf("%.1lf, ", (*it).z);
	}
	printf("\n");
}