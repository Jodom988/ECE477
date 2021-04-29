#include <stdio.h>
#include <stdint.h>
#include <sys/time.h>
#include <opencv2/opencv.hpp>
#include <opencv2/core/types.hpp>
#include <list>
#include <iostream>
#include <thread>

#include <sys/socket.h> 
#include <sys/ioctl.h>
#include <netdb.h> 
#include <sys/types.h> 
#include <netinet/in.h> 
#include <arpa/inet.h>
#include <unistd.h>

#define THRESH 50
#define THREADS 4
#define N 4
#define MESSAGE_SIZE 1000000

#define EXIT 0x95
#define PROC_FRAME 0x96
#define XY_DATA 0x97
#define BASE_FRAME 0x98
#define SCRN_BOUNDS 0x99

#define READ_ERR -1
#define READ_SUCCESS 0

#define PT_NOT_FOUND 0xFFFFFFFF

using namespace cv;
using namespace std;

uchar* get_pixel(Mat img, int x, int y);

void add_to_list_sorted(std::list<cv::Point3d> & largest_vals, Point3d pt, int thresh, int max);
void detect_in_frame_worker_skips(Mat img, Mat base, std::list<cv::Point3d> & largest_vals, int min_col, int max_col, int min_row, int max_row);
Point detect_in_frame_threads(Mat img, Mat base, double top_pct, double bottom_pct, double left_pct, double right_pct);
int read_message(int socketfd);
int read_img_socket(int socketfd, Mat & dest);

Point test_detect_in_frame(Mat img, Mat base);
void add_lines(Mat img, int row, int col, int w);

FILE* log_fd;
int main(int argc, char** argv)
{
	log_fd = fopen("/home/pi/Repos/ECE477/laser_detector/rel/build/ProcessFrame.log", "w");
	
	if (log_fd == NULL)
	{
		printf("Unable to create log file");
		return 1;
	}
	if (argc != 2)
	{
		fprintf(log_fd, "Propper Usage: ProcessFrame <port>\n");
		return 1;
	}

	int port = atoi(argv[1]);

	//Create socket
	int socketfd;
	struct sockaddr_in servAddr;

	if((socketfd = socket(AF_INET, SOCK_STREAM, 0)) == -1){
		fprintf(log_fd, "Could not create socket\n");
		return 1;
	} else {
		fprintf(log_fd, "Socket created\n");
	}

	//Make connection
	servAddr.sin_family = AF_INET;
	servAddr.sin_port = htons(port);
	servAddr.sin_addr.s_addr = inet_addr("127.0.0.1");
	bzero(&(servAddr.sin_zero), 8);

	fprintf(log_fd, "Connecting... ");
	if (connect(socketfd, (struct sockaddr *)&servAddr, sizeof(servAddr))  == -1) {
		fprintf(log_fd, "\nConnect Failed\n");
	}
	fprintf(log_fd, "Done!\n");

	Mat base_frame;
	Mat frame;
	uint8_t header;
	char send_msg[16];
	Point pos;

	fd_set referenced_fds;

	double top = 0;
	double bottom = 1;
	double left = 0;
	double right = 1;

	while (true)
	{
		//Wait for request (select blocks until resource is ready)
		FD_ZERO(&referenced_fds);
		FD_SET(socketfd,&referenced_fds);
		select(socketfd + 1, &referenced_fds, NULL, NULL, NULL);

		if(FD_ISSET(socketfd, &referenced_fds)){ //Process Request

			header = read_message(socketfd);
			
			if (header == EXIT)
			{
				fprintf(log_fd, "Received code exit, exiting gracefully\n");
				break;
			} else if (header == PROC_FRAME) {
				fprintf(log_fd, "Process frame code\n");

				read_img_socket(socketfd, std::ref(frame));

				//Process frame
				//pos = test_detect_in_frame(frame, base_frame);
				pos = detect_in_frame_threads(frame, base_frame, top, bottom, left, right);

				// Send data back
				send_msg[0] = XY_DATA;
				//Put 4 bytes for x and y
				for (int i = 0; i < 4; i++)
				{
					send_msg[1 + i] = ((char *) &(pos.x))[i];
					send_msg[5 + i] = ((char *) &(pos.y))[i];
				}
				send(socketfd, send_msg, 9, 0);

			} else if (header == BASE_FRAME) {
				fprintf(log_fd, "Base frame code\n");
				//Get frame from socket
				read_img_socket(socketfd, std::ref(base_frame));

			} else if (header == SCRN_BOUNDS) {
				fprintf(log_fd, "Screen bounds code\n");
				uint16_t edges[4];
				if(read(socketfd, &(edges[0]), 8) < 0){
					fprintf(log_fd, "Error reading screen bounds data\n");
					break;
				}

				top = edges[0] / 4095.0;
				bottom = edges[1] / 4095.0;
				left = edges[2] / 4095.0;
				right = edges[3] / 4095.0;

				fprintf(log_fd, "Vertical: [%.2f, %.2f], Horizontal: [%.2f, %.2f\n]", top, bottom, left, right);

				Mat tmp_img = Mat(base_frame);
				add_lines(tmp_img, top*base_frame.size().height, left*base_frame.size().width, 0);
				add_lines(tmp_img, bottom*base_frame.size().height, right*base_frame.size().width, 0);
				vector<int> compression_params;
				compression_params.push_back(IMWRITE_JPEG_QUALITY);
				compression_params.push_back(95);
				cv::imwrite("borders.jpg", tmp_img, compression_params);

			}else if (header == READ_ERR) {
				fprintf(log_fd, "Read error when interpreting message header, exiting gracefully... \n");
				break;
			} else if (header == 0x00) {
				fprintf(log_fd, "Lost connection from other side\n");
				break;
			} 
			else {
				fprintf(log_fd, "Unrecognized code (%X), exiting...\n", header);
				break;
			}
		}
		fclose(log_fd);
		log_fd = fopen("/home/pi/Repos/ECE477/laser_detector/rel/build/ProcessFrame.log", "a");
	}

	fclose(log_fd);

	return 0;
}


int read_message(int socketfd){
	uint8_t header;
	if(read(socketfd, &(header), 1) < 0){
		return READ_ERR;
	}

	return header;
}

int read_img_socket(int socketfd, Mat & dest)
{
	uint32_t img_size;

	if(read(socketfd, &(img_size), 4) < 0){
		fprintf(log_fd, "Could not read image size correctly\n");
		return READ_ERR;
	}

	uint32_t read_progress = 0;
	uint32_t buff_size;

	std::vector<char> img_data(img_size);

	while (read_progress < img_size)
	{
		if(ioctl(socketfd, FIONREAD, &buff_size) == -1){
			fprintf(log_fd, "Error reading message size\n");
			return READ_ERR;
		}
		if(read(socketfd, &(img_data[read_progress]), buff_size) < 0){
			fprintf(log_fd, "Error reading message data\n");
			return READ_ERR;
		}
		read_progress += buff_size;
	}

	
	dest = imdecode(Mat(img_data), 1);

/*	vector<int> compression_params;
	compression_params.push_back(IMWRITE_JPEG_QUALITY);
	compression_params.push_back(95);
	cv::imwrite("rx_img.jpg", dest, compression_params);*/

	return READ_SUCCESS;
}

void add_to_list_sorted(std::list<cv::Point3d> & largest_vals, Point3d pt, int thresh, int max)
{
	for (std::list<Point3d>::iterator it = largest_vals.begin(); it != largest_vals.end(); it++){
		if (pt.z > (*it).z)
		{
			largest_vals.insert(it, pt);
			if (largest_vals.size() > max)
			{
				largest_vals.pop_back();
			}
			break;
		}
	}
}

void detect_in_frame_worker_skips(Mat img, Mat base, std::list<cv::Point3d> & largest_vals, int min_col, int max_col, int min_row, int max_row){
	uint16_t height = img.size().height;
	uint16_t width = img.size().width;

	largest_vals.push_front(cv::Point3d(0, 0, THRESH));

	int val;
	
	for (int row_idx = min_row; row_idx < max_row; row_idx+=2)
	{
		for (int col_idx = min_col; col_idx < max_col; col_idx++)
		{
			// Calculate diff
			val = get_pixel(img, col_idx, row_idx)[1];
			//val = get_pixel(img, col_idx, row_idx)[1] - get_pixel(base, col_idx, row_idx)[1];

			// Add to list
			if (val > largest_vals.back().z)
			{
				Point3d pt = Point3d(col_idx, row_idx, val);
				add_to_list_sorted(std::ref(largest_vals), pt, THRESH, N);

				//Check above and add to list
				if (row_idx >= 1)
				{
					val = get_pixel(img, col_idx, row_idx-1)[1] - get_pixel(base, col_idx, row_idx-1)[1];

					if (val > largest_vals.back().z)
					{
						Point3d pt = Point3d(col_idx, row_idx-1, val);
						add_to_list_sorted(std::ref(largest_vals), pt, THRESH, N);
					}
				}

				//Check below and add to list
				if (row_idx <= height-2)
				{
					val = get_pixel(img, col_idx, row_idx+1)[1] - get_pixel(base, col_idx, row_idx+1)[1];
					if (val > largest_vals.back().z)
					{
						Point3d pt = Point3d(col_idx, row_idx+1, val);
						add_to_list_sorted(std::ref(largest_vals), pt, THRESH, N);
					}
				}

			}

		}
	}

	if (largest_vals.back().z == THRESH){
		largest_vals.pop_back();
	}

}

Point detect_in_frame_threads(Mat img, Mat base, double top_pct, double bottom_pct, double left_pct, double right_pct){
	std::thread workers[THREADS];
	std::list<cv::Point3d> queues[THREADS];	

	Point3d maxes[N];

	int min_col;
	const int thickness = (img.size().width * (right_pct - left_pct)) / THREADS;
	int max_col;

	min_col = img.size().width * left_pct;
	max_col = min_col + thickness;

	int min_row = img.size().height * top_pct;
	int max_row = img.size().height * bottom_pct;

	
	for (int i = 0; i < THREADS; ++i)
	{
		fprintf(log_fd, "Col Range: [%d, %d], Row Range: [%d, %d]\n", min_col, max_col, min_row, max_row);
		workers[i] = std::thread(detect_in_frame_worker_skips, img, base, std::ref(queues[i]), min_col, max_col, min_row, max_row);

		min_col = max_col + 1;

		if (i == THREADS - 2)
		{
			max_col = img.size().width;
		} else
		{
			max_col = min_col + thickness;
		}
	}

	int strips_with_multiple_count = 0;
	int strip_with_multiple;
	for (int i = 0; i < THREADS; i++)
	{
		workers[i].join();
		if (queues[i].size() > 0)
		{
			strips_with_multiple_count++;
			strip_with_multiple = i;
		}
	}
	printf("Threads joined!\n");

	if (strips_with_multiple_count == 0)
	{ //Not found 
		return Point(PT_NOT_FOUND, PT_NOT_FOUND);
	} else if (0 && strips_with_multiple_count == 1)
	{
		//One thread found points
		Point3d sum;
		int pts_found = 0;
		for (std::list<Point3d>::iterator it = queues[strip_with_multiple].begin(); it != queues[strip_with_multiple].end(); it++){
			sum += *it;
			pts_found++;
		}

		int row_avg = sum.y / pts_found;
		int col_avg = sum.x / pts_found;

		return Point(col_avg, row_avg);
	} else {
		// Multiple threads found points
		printf("Multiple found\n");
		Point3d sum;
		int pts_found = 0;
		for (int i = 0; i < N; i++)
		{
			int largest_idx = -1;
			for (int j = 0; j < THREADS; j++)
			{
				if (queues[j].size() != 0)
				{
					largest_idx = j;
					break;
				}
			}

			if (largest_idx == -1){
				break;
			}else{

				for(int j = largest_idx; j < THREADS; j++)
				{
					if(queues[j].size() > 0)
					{
						if (queues[j].front().z > queues[largest_idx].front().z)
						{
							largest_idx = j;
						}
					}
				}

				sum += queues[largest_idx].front();
				queues[largest_idx].pop_front();
				pts_found ++;
			}
		}

		printf("Returning\n");

		int row_avg = sum.y / pts_found;
		int col_avg = sum.x / pts_found;
		return Point(col_avg, row_avg);
	}
	
}


Point test_detect_in_frame(Mat img, Mat base){
	uint16_t height = img.size().height;
	uint16_t width = img.size().width;

	Mat new_img(height, width*3, CV_8UC(3));

	std::list<cv::Point3d> largest_vals;
	largest_vals.push_front(cv::Point3d(0, 0, THRESH));

	fprintf(log_fd, "img: %d %d, base: %d %d\n", img.size().width, img.size().height, base.size().width, base.size().height);

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

	if (largest_vals.size() > N / 2)
	{
		for (std::list<Point3d>::iterator it = largest_vals.begin(); it != largest_vals.end(); it++){
			sum += *it;
		}

		int row_avg = sum.y / N;
		int col_avg = sum.x / N;

		add_lines(new_img, row_avg, col_avg, 4);

		vector<int> compression_params;
	    compression_params.push_back(IMWRITE_JPEG_QUALITY);
	    compression_params.push_back(95);

	    imwrite("./proc_img.jpg", new_img, compression_params);

		return Point(col_avg, row_avg);

	} else {
		return Point(-1, -1);
	}
	



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