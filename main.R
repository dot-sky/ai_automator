# Load required library
library(rvest)

# Website URL
url <- "https://www.uebelhorcommercialtruck.com/meet-our-staff/"

# Read the HTML from the page
html <- read_html(url)

# Find elements whose id or class contains "staff"
candidates <- html %>% html_elements('[id*="staff"], [class*="staff"]')

# Select the first candidate node
main_staff_node <- candidates[[1]]

# Convert the node to HTML (as text)
main_staff_html <- as.character(main_staff_node)

# Save the HTML as text to a .txt file
write(main_staff_html, file = "staff_container.txt")

# Optional message
cat("Content saved to staff_container.txt\n")
