def count_scoring_combinations(target_points):
    """
    Count the number of different combinations to score exactly target_points
    using free throws (1 pt), 2-point field goals, and 3-point field goals.

    Args:
        target_points: The target score to reach

    Returns:
        Number of different combinations to reach the target score
    """
    # dp[i] = number of ways to score exactly i points
    dp = [0] * (target_points + 1)

    # Base case: there's one way to score 0 points (score nothing)
    dp[0] = 1

    # The scoring options available
    scoring_options = [1, 2, 3]  # free throw, 2-pt FG, 3-pt FG

    # For each scoring option
    for points in scoring_options:
        # Update all achievable scores using this scoring option
        for current_score in range(points, target_points + 1):
            # Add the number of ways to score (current_score - points)
            # because we can reach current_score by adding 'points' to that previous score
            dp[current_score] += dp[current_score - points]

    return dp[target_points]


def count_scoring_combinations_with_details(target_points):
    """
    Same as above but prints the DP table for visualization.
    """
    dp = [0] * (target_points + 1)
    dp[0] = 1

    scoring_options = [1, 2, 3]

    print(f"Finding combinations to score {target_points} points\n")
    print(f"Initial state: {dp}\n")

    for points in scoring_options:
        print(f"Processing {points}-point scoring option:")
        for current_score in range(points, target_points + 1):
            print(f"Checking Range {points}, {target_points + 1}")
            old_value = dp[current_score]
            dp[current_score] += dp[current_score - points]
            if dp[current_score] != old_value:
                print(
                    f"  dp[{current_score}] = {old_value} + dp[{current_score - points}] = {dp[current_score]}"
                )
                print(f"dp is now {dp}")
        print(f"State after {points}-pt: {dp}\n")

    return dp[target_points]


# Example usage
if __name__ == "__main__":
    # Test with some examples
    test_scores = [15]

    for score in test_scores:
        result = count_scoring_combinations(score)
        print(f"Number of ways to score {score} points: {result}")

    print("\n" + "=" * 60)
    print("DETAILED WALKTHROUGH for 6 points:")
    print("=" * 60 + "\n")

    result = count_scoring_combinations_with_details(6)
    print(f"Final answer: {result} different combinations to score 6 points")
