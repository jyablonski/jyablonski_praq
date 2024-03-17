#include <iostream>

void doubleArrayValues(int arr[], int size) {
    for (int i = 0; i < size; ++i) {
        arr[i] *= 2;
    }
}

int main() {
    const int SIZE = 5;
    int arr[SIZE] = {1, 2, 3, 4, 5};

    std::cout << "Original array:";
    for (int i = 0; i < SIZE; ++i) {
        std::cout << " " << arr[i];
    }
    std::cout << std::endl;

    doubleArrayValues(arr, SIZE);

    std::cout << "Array after doubling:";
    for (int i = 0; i < SIZE; ++i) {
        std::cout << " " << arr[i];
    }
    std::cout << std::endl;

    return 0;
}