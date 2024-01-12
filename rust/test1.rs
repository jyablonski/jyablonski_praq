fn mystery_function(input: &str) -> i32 {
    let mysteries = "aeiouAEIOU";
    input.chars().filter(|c| mysteries.contains(*c)).count() as i32
}

fn main(){
    let input_string = "Hello, world!";
    let mystery_count = mystery_function(&input_string);
    println!("The number of mysteries in '{}' is {}", input_string, mystery_count);
}