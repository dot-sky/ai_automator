library(rvest)

args <- commandArgs(trailingOnly = TRUE)
url <- args[1]

# Read HTML from the page
html <- read_html(url)

# Find 
candidates <- html %>% html_elements('[class*="staff-page"], [id*="staff"], [class*="staff"], [class*="team-member"], [class*="staffList"] , [class*="meet_our_staff_wrap"]')

# Select the best candidate node
if (length(candidates) == 0) {
  stop("No candidates found for staff container.")
}

# Count how many staff members each candidate contains
counts <- sapply(candidates, function(node) {
  # Adjust the selector inside to match actual staff member elements
  length(html_elements(node, '[class*="staff"], [class*="staff-card"], [class*="team-member"], [class*="staff-item"], [class*="employee_wrap_staff"]'))
})

# Pick the node with the maximum count
best_index <- which.max(counts)
main_staff_node <- candidates[[best_index]]

# Convert the node to HTML (as text)
main_staff_html <- as.character(main_staff_node)

# Save the HTML as text to a .txt file
output_file <- file.path("data", "extracted_html", "staff_container.txt")

write(main_staff_html, file = output_file)

# Optional message
cat("Content saved to staff_container.txt\n")
