// this is a comment boi

// lets us get user input from a user, or print something to console (Stdout)
# include <iostream>
# include <cstdlib>

using namespace std;


int main () {

    // int file_size; <--- this is bad news bears

    // initialize this mfer
    int loops = 2;
    int file_size = 100;
    int temp = loops;
    
    file_size = temp;

    // const prevents you from modying a variable in the future
    const double pi = 3.14;
    // pi = 2; <--- this will cause compilation to fail

    std::cout << "buttcheeks";
    std::cout << file_size;

    std::cout << pi;

    int x = 10;
    int y = 3;
    int z = x / y;

    std::cout << "\n\n";
    
    // 10 / 3 is 3 apparently in c++
    std::cout << z;

    double xx = 10;
    int yy = 3;
    double zz = xx / y;

    std::cout << "\n\n";
    std::cout << zz;

    std::cout << "\n\n";

    int ab = 1;
    int bc = ab++; // ab = 2, bc is still 1

    std::cout << ab;
    std::cout << "\n\n";
    std::cout << bc;

    int yap = (2 + 3) * 9;

    std::cout << "\n\n" << yap << "new buttcheeks" << std::endl;

    cout << "wow using namespace std deez nuts why in the fuck did we not turn that on before huh" << endl;

    cout << "Enter a Value pls: ";
    int user_input;
    cin >> user_input;
    cout << "Hey thx for inputting " << user_input << endl;

    double sale_price = 99.99;
    float interest_rate = 3.67f;
    long file_size_2 = 90000L;
    char letter = 'a';
    auto my_char = 'b';

    // rand numer, but this will always have the same seed unless we give it a seed
    long elapsed_seconds = time(0);
    srand(elapsed_seconds);
    int rand_number = rand();
    cout << rand_number << endl;

    return 0;
    
}