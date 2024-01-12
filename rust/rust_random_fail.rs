fn count_characters(s: &str, c: char) -> usize {
    s.chars().filter(|x| *x == c).count()
}

fn main() {
    let mut rng = rand::thread_rng();
    if rng.gen_bool(0.5) {
        count_characters("Hello world", 'o');
    } else {
        count_characters("Hello world", 23);
    }
}