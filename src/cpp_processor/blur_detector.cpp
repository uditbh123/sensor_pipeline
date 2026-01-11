#include <iostream>
#include <vector>
#include <string>
#include <numeric>
#include <cmath>
#include "sqlite3.h"

// --- CONFIG ---
const int WIDTH = 640;
const int HEIGHT = 480;

// --- STEP 1: RGB to Grayscale Conversion ---
// This prevents the detector from confusing "Color Changes" with "Sharp Edges"
std::vector<uint8_t> toGrayscale(const std::vector<uint8_t>& rgb, int w, int h) {
    std::vector<uint8_t> gray;
    gray.reserve(w * h);

    // Loop through pixels (jumping 3 bytes at a time for R, G, B)
    for (size_t i = 0; i < rgb.size(); i += 3) {
        if (i + 2 >= rgb.size()) break; // Safety check

        int r = rgb[i];
        int g = rgb[i + 1];
        int b = rgb[i + 2];

        // Luminance Formula: 0.299*R + 0.587*G + 0.114*B
        // (Green contributes most because human eyes are sensitive to it)
        uint8_t val = (uint8_t)(0.299 * r + 0.587 * g + 0.114 * b);
        gray.push_back(val);
    }
    return gray;
}

// --- STEP 2: Variance Helper ---
double computeVariance(const std::vector<double>& data) {
    if (data.empty()) return 0.0;
    double sum = 0.0;
    for (double val : data) sum += val;
    double mean = sum / data.size();
    
    double sqDiff = 0.0;
    for (double val : data) sqDiff += (val - mean) * (val - mean);
    return sqDiff / data.size();
}

// --- STEP 3: Laplacian Convolution ---
double calculateLaplacianVariance(const std::vector<uint8_t>& img, int w, int h) {
    std::vector<double> edgeValues;
    edgeValues.reserve((w - 2) * (h - 2)); 

    // Note: 'img' is now a 1-channel Grayscale image
    for (int y = 1; y < h - 1; y++) {
        for (int x = 1; x < w - 1; x++) {
            int center = img[y * w + x];
            int up     = img[(y - 1) * w + x];
            int down   = img[(y + 1) * w + x];
            int left   = img[y * w + (x - 1)];
            int right  = img[y * w + (x + 1)];

            double val = (up + down + left + right) - (4 * center);
            edgeValues.push_back(val);
        }
    }
    return computeVariance(edgeValues);
}

int main(int argc, char** argv) {
    if (argc < 2) return 1;

    std::string dbPath = argv[1];
    sqlite3* db;
    if (sqlite3_open(dbPath.c_str(), &db)) return 1;

    const char* sql = "SELECT timestamp, data FROM messages";
    sqlite3_stmt* stmt;
    sqlite3_prepare_v2(db, sql, -1, &stmt, 0);

    std::cout << "--- ROBOTICS DATA PIPELINE ---" << std::endl;
    std::cout << "Pipeline: Raw RGB -> Grayscale -> Laplacian Edge Detection" << std::endl;
    std::cout << "----------------------------------------" << std::endl;

    int i = 0;
    int correct = 0;
    int total = 0;

    while (sqlite3_step(stmt) == SQLITE_ROW) {
        const uint8_t* blobPtr = (const uint8_t*)sqlite3_column_blob(stmt, 1);
        int blobSize = sqlite3_column_bytes(stmt, 1);
        std::vector<uint8_t> rawData(blobPtr, blobPtr + blobSize);

        // 1. Pre-process (Critical Fix!)
        std::vector<uint8_t> grayImage = toGrayscale(rawData, WIDTH, HEIGHT);

        // 2. Compute Score
        double score = calculateLaplacianVariance(grayImage, WIDTH, HEIGHT);

        // 3. Classify
        // Grayscale variance is lower than RGB. Let's try a threshold of 100.0
        // You will likely see Sharp > 300, Blur < 50
        std::string status = (score < 100.0) ? "BLURRY" : "SHARP"; 

        // 4. Validate
        std::string gt = (i < 50) ? "SHARP" : "BLURRY";
        bool is_ok = (status == gt);
        if (is_ok) correct++;
        total++;

        std::cout << "Frame " << i 
                  << " | Score: " << (int)score 
                  << " | Pred: " << status 
                  << " | GT: " << gt 
                  << (is_ok ? " [OK]" : " [FAIL]") 
                  << std::endl;
        i++;
    }

    std::cout << "----------------------------------------" << std::endl;
    std::cout << "ACCURACY: " << ((double)correct/total * 100.0) << "%" << std::endl;

    sqlite3_finalize(stmt);
    sqlite3_close(db);
    return 0;
}