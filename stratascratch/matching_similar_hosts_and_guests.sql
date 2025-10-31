/* https://platform.stratascratch.com/coding/10078-find-matching-hosts-and-guests-in-a-way-that-they-are-both-of-the-same-gender-and-nationality?code_type=1

Find matching hosts and guests pairs in a way that they are both of the same gender and nationality.
Output the host id and the guest id of matched pair. */

-- fuicking sigh bro
select distinct
    airbnb_hosts.host_id,
    airbnb_guests.guest_id
from airbnb_hosts
inner join airbnb_guests
    on airbnb_hosts.nationality = airbnb_guests.nationality
    and airbnb_hosts.gender = airbnb_guests.gender