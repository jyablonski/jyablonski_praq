# Given a valid (IPv4) IP address, return a defanged version of that IP address.

# A defanged IP address replaces every period "." with "[.]".


# what the fuck is this ?
def solution(address: str) -> str:
    return address.replace(".", "[.]")


address1 = "1.1.1.1"
address2 = "255.100.50.1"

solution(address=address1)
solution(address=address2)
