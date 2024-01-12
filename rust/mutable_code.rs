// Louis owns the console
let mut console_high_score = 8999;

{   // I borrow the console for this block
    
    let y = &mut console_high_score;

    // I'm ruining the high score here by performing an action (mutation)
    *y += 2;

}  // At the end of this block, I return it to Louis

println!("console_high_score is now {}", console_high_score);