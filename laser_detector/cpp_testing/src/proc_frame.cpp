#include <stdio.h>
#include <stdint.h>
#include <sys/time.h>
#include <opencv2/opencv.hpp>
#include <opencv2/core/types.hpp>
#include <list>
#include <iostream>
#include <thread>

#define THRESH 50
#define THREADS 4

using namespace cv;
using namespace std;

long current_time_millis();
Point test_detect_in_frame(Mat img, Mat base);
Point detect_in_frame(Mat img, Mat base);
void print_point(Point p);
uchar* get_pixel(Mat img, int x, int y);
void printlist(std::list<Point3d> list);
void add_lines(Mat img, int row, int col, int w);

Point detect_in_frame_worker(Mat img, Mat base, std::list<cv::Point3d> largest_vals, int min_col, int max_col);
Point detect_in_frame_thread(Mat img, Mat base);

int main(int argc, char** argv)
{
	// Test video
	if (1)
	{
		VideoCapture cap(".././ir-laser-test-1mw-24ma-2.mjpeg");
		//VideoCapture cap(0);

		int fourcc = VideoWriter::fourcc('X','V','I','D');
		int width = 640;
		int height = 480;
		//VideoWriter out("./outcpp.avi", fourcc, 30, Size(640,480));

		FILE* times_fptr = fopen("../../scripts/data/times_proc_frame.txt", "w");

		int i = 0;
		Mat frame;
		Mat base_frame;
		Point pos(0, 0);
		while(1)
		{
			cap.read(frame);
			if(frame.empty())
			{
				if (i == 0)
				{
					printf("Couldn't read first frame\n");
				}
				break;
			}
			if(i == 0)
			{
				base_frame = frame.clone();
			}

			int start = current_time_millis();
			pos = detect_in_frame_thread(frame, base_frame);
			int diff = current_time_millis() - start;

			fprintf(times_fptr, "%d\n", diff);

			printf("%d (%d, %d) \n", i, pos.x, pos.y);

			add_lines(frame, pos.y, pos.x, 3);
			//out.write(frame);

			i++;

		}

		if (times_fptr != NULL)
		{
			fclose(times_fptr);
		}
	}

	// Test single frame
	if (0)
	{
		Mat image, base;
		base = cv::imread("../../imgs/base.jpg", 1);
		image = cv::imread("../../imgs/ir-laser-1mw-24ma.jpg", 1);

		uint16_t rows = image.size().height;
		uint16_t cols = image.size().width;

		long start = current_time_millis();
		test_detect_in_frame(image, base);
		long diff = current_time_millis() - start;
		//printf("Time Elapsed %ld\n", diff);
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

Point detect_in_frame_worker(Mat img, Mat base, std::list<cv::Point3d> largest_vals, int min_col, int max_col){
	uint16_t height = img.size().height;
	uint16_t width = img.size().width;

	int N = 4;

	//largest_vals.push_front(cv::Point3d(0, 0, THRESH));
	
	for (int row_idx = 0; row_idx < height; row_idx++)
	{
		for (int col_idx = min_col; col_idx < max_col; col_idx++)
		{
			// Calculate diff
			int val = get_pixel(img, col_idx, row_idx)[1] - get_pixel(base, col_idx, row_idx)[1];
			// Add to list
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

Point detect_in_frame_thread(Mat img, Mat base){
	std::thread workers[THREADS];
	std::list<cv::Point3d> queues[THREADS];	

	int min_col;
	const int thickness = img.size().width / THREADS;
	int max_col;

	min_col = 0;
	max_col = min_col + thickness;

	for (int i = 0; i < THREADS; ++i)
	{
		queues[i].push_front(cv::Point3d(0, 0, THRESH));
		workers[i] = std::thread(detect_in_frame_worker, img, base, queues[i], min_col, max_col);

		min_col = max_col + 1;

		if (i == THREADS - 2)
		{
			max_col = img.size().width;
		} else
		{
			max_col = min_col + thickness;
		}
	}


	for (int i = 0; i < THREADS; i++)
	{
		workers[i].join();
	}
}

Point detect_in_frame(Mat img, Mat base){
	uint16_t height = img.size().height;
	uint16_t width = img.size().width;

	int N = 4;

	std::list<cv::Point3d> largest_vals;
	largest_vals.push_front(cv::Point3d(0, 0, THRESH));
	
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

	add_lines(new_img, row_avg, col_avg, 4);

	namedWindow("Display Image", cv::WINDOW_AUTOSIZE);
	imshow("Display Image", new_img);

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

	cv::line(img, Point(0, row+w), Point(width, row+w), {0, 255, 0}, 1);
	cv::line(img, Point(0, row-w), Point(width, row-w), {0, 255, 0}, 1);

	cv::line(img, Point(col-w, 0), Point(col-w, height), {0, 255, 0}, 1);
	cv::line(img, Point(col+w, 0), Point(col+w, height), {0, 255, 0}, 1);
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