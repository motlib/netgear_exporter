# Netgear Login

- Login page has form posting to login.cgi
  Login form has field `rand` with random value. Seems always to be `1450459452`
- Send back form item "password" with encrypted value
- Encryption:
  - Merge password with characters from random number P1 
  