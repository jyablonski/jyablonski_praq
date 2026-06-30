fn main() {
    let x; // declare "x"
    x = 42; // assign 42 to "x"
    // let x = 43;  - use this though
    println!("Hello, {}!", x);

    let y: i32; // `i32` is a signed 32-bit integer
    y = -3;
    println!("Hello {}", y);

    // Names that start with an underscore are regular names, it's just that the compiler won't warn about them being unused
    let _test = 42;

    // Rust has tuples, which you can think of as "fixed-length collections of values of different types".
    let pair = ('a', 17);
    pair.0; // this is 'a'
    pair.1; // this is 17

    let _pair2: (char, i32) = ('a', 17);

    let x = vec![1, 2, 3, 4, 5, 6, 7, 8]
    .iter()
    .map(|x| x + 3)
    .fold(0, |x, y| x + y);

    println!("{}", x);

    fn greet() {
        println!("Hi there!");
    }
}
