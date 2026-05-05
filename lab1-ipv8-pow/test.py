from pow import mine_nonce

email = "J.J.R.Duggins-1@student.tudelft.nl"
github_url = "https://github.com/jayran-d/blockchain-engineering-labs"

nonce = mine_nonce(email, github_url)
print(nonce)
