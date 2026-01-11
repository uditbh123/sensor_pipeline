#include <iostream>
#include <vector>
#include <string>
#include "sqlite3.h"

// This helper function handles errors.
// If the database complains, it prints the error and shuts down.
void check_db_error(int rc, char* err_msg) {
    if (rc != SQLITE_OK) {
        std::cerr << "SQL Error: " <<err_msg << std::endl;
        sqlite3_free(err_msg);
        exit(1);
    }
}

int main(int argc, char* argv[]) {
    std::cout << "--- C++ ROBOT DATA READER ---" << std::endl;

    // 1. Get the database path from the command line
    if (argc < 2) {
        std::cerr << "Usage: " << argv[0] << "<path_to_bag.db3>" <<std::endl;
        return 1;
    }
    std::string db_path = argv[1];

    // 2. open the database
    sqlite3* db;
    int rc = sqlite3_open(db_path.c_str(), &db);

    if (rc) {
        std::cerr << "Can't open database: " << sqlite3_errmsg(db) << std::endl;
        return 1;
    } else {
        std::cout << "Opened database successfully: " << db_path << std::endl;
    }

    // 3. prepare the SQL query
    // Here It requires the timestamp and the raw binary data (the image)
    const char* sql = "SELECT timestamp, data FROM messages ORDER By timestamp ASC;";
    sqlite3_stmt* stmt;

    rc = sqlite3_prepare_v2(db, sql, -1, &stmt, 0);

    if (rc != SQLITE_OK) {
        std::cerr << "Failed to fetch data: " << sqlite3_errmsg(db) << std::endl;
        return 1;
    }

    // 4. Loop through the rows (Processing the stream)
    int count = 0;
    std::cout << "\n--- READING MESSAGES ---" << std::endl;

    while (sqlite3_step(stmt) == SQLITE_ROW) {
        // Column 0: Timestamp (Int 64)
        long long timestamp = sqlite3_column_int64(stmt, 0);

        // Column 1: The Raw Image Data (Blob/Bytes)
        const void* blob_data = sqlite3_column_blob(stmt, 1);
        int blob_size = sqlite3_column_bytes(stmt, 1);

        // Just print stats for now 
        std::cout << "Frame " << count
                  << " | Time: " << timestamp
                  << " | Size: " << blob_size << " bytes" << std::endl;
        
        count++;
    }

    // 5. Cleanup
    sqlite3_finalize(stmt);
    sqlite3_close(db);

    std::cout << "\nSUCCESS: Processed " << count << " frames." << std::endl;
    return 0;
}