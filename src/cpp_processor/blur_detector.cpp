#include <iostream>
#include <vector>
#include <string>
#include <cmath>     
#include <numeric>   
#include "sqlite3.h"

// --- CONFIGURATION ---
const int HEADER_SIZE = 68; // Skip the ROS 2 metadata bytes
const int WIDTH = 100;      
const int HEIGHT = 100;

// --- MATH HELPER: Convert RGB to Grayscale ---
std::vector<unsigned char> to_grayscale(const unsigned char* rgb_data, int total_pixels) {
    std::vector<unsigned char> gray(total_pixels);
    for (int i = 0; i < total_pixels; ++i) {
        // Simple luminance formula
        int r = rgb_data[i * 3];
        int g = rgb_data[i * 3 + 1];
        int b = rgb_data[i * 3 + 2];
        gray[i] = static_cast<unsigned char>(0.299 * r + 0.587 * g + 0.114 * b);
    }
    return gray;
}

// --- ALGORITHM: Laplacian Variance (Blur Detection) ---
double calculate_blur_score(const std::vector<unsigned char>& img) {
    if (img.empty()) return 0.0;

    std::vector<int> laplacian_values;
    double mean = 0.0;
    
    // Convolve with Laplacian Kernel (Edge Detection)
    // [ 0,  1, 0 ]
    // [ 1, -4, 1 ]
    // [ 0,  1, 0 ]
    for (int y = 1; y < HEIGHT - 1; ++y) {
        for (int x = 1; x < WIDTH - 1; ++x) {
            int idx = y * WIDTH + x;
            
            int val = 4 * img[idx] 
                    - img[idx - WIDTH] // Up
                    - img[idx + WIDTH] // Down
                    - img[idx - 1]     // Left
                    - img[idx + 1];    // Right
            
            laplacian_values.push_back(val);
            mean += val;
        }
    }

    mean /= laplacian_values.size();

    // Calculate Variance
    double variance = 0.0;
    for (int val : laplacian_values) {
        variance += (val - mean) * (val - mean);
    }
    return variance / laplacian_values.size();
}

int main(int argc, char* argv[]) {
    std::cout << "--- ROBOTICS BLUR DETECTOR STARTED ---" << std::endl;

    if (argc < 2) {
        std::cerr << "Usage: " << argv[0] << " <path_to_bag.db3>" << std::endl;
        return 1;
    }

    sqlite3* db;
    if (sqlite3_open(argv[1], &db)) {
        std::cerr << "Error opening DB: " << sqlite3_errmsg(db) << std::endl;
        return 1;
    }

    const char* sql = "SELECT timestamp, data FROM messages ORDER BY timestamp ASC;";
    sqlite3_stmt* stmt;
    sqlite3_prepare_v2(db, sql, -1, &stmt, 0);

    std::cout << "\nProcessing Frames..." << std::endl;
    std::cout << "----------------------------------------" << std::endl;

    int count = 0;
    while (sqlite3_step(stmt) == SQLITE_ROW) {
        // Read Data
        const unsigned char* blob = (const unsigned char*)sqlite3_column_blob(stmt, 1);
        int size = sqlite3_column_bytes(stmt, 1);

        if (size <= HEADER_SIZE) continue;

        // 1. POINTER ARITHMETIC: Skip Header
        const unsigned char* pixel_start = blob + HEADER_SIZE;
        int pixel_count = (size - HEADER_SIZE) / 3; 

        // 2. Process
        std::vector<unsigned char> gray_img = to_grayscale(pixel_start, pixel_count);
        double score = calculate_blur_score(gray_img);

        // 3. Evaluate
        std::string status = (score < 100.0) ? "BLURRY ❌" : "SHARP   ✅";
        
        std::cout << "Frame " << count 
                  << " | Score: " << score 
                  << " | Status: " << status << std::endl;
        
        count++;
    }

    sqlite3_finalize(stmt);
    sqlite3_close(db);
    return 0;
}