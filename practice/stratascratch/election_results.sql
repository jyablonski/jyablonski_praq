/* https://platform.stratascratch.com/coding/2099-election-results?code_type=1

The election is conducted in a city and everyone can vote for one or more candidates, or choose not to vote at all.
Each person has 1 vote so if they vote for multiple candidates, their vote gets equally split across these
candidates. For example, if a person votes for 2 candidates, these candidates receive an equivalent of 0.5
vote each. Some voters have chosen not to vote, which explains the blank entries in the dataset.

Find out who got the most votes and won the election. Output the name of the candidate or multiple names in case of a tie.

To avoid issues with a floating-point error you can round the number of votes received by a candidate to 3 decimal places. */

-- count up all votes by every voter so we can do a pct / total calc later
with user_votes as (
    select
        voter,
        count(*) as total_votes
    from voting_results
    group by voter
),

-- then join those votes back and do a pct of total calc
user_vote_pcts as (
    select
        voting_results.voter,
        voting_results.candidate,
        user_votes.total_votes,
        1.0 / user_votes.total_votes as candidate_votes
    from voting_results
    inner join user_votes
        on voting_results.voter = user_votes.voter
)

-- then sum by that candidate_votes field, removing the null candidates
-- and ordering by the candidate who had the most
select
    candidate
from user_vote_pcts
where candidate != ''
group by 1
order by sum(candidate_votes) desc
limit 1