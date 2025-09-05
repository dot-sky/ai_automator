library(rvest)

args <- commandArgs(trailingOnly = TRUE)
url <- args[1]
output_file <- args[2]

html <- read_html(url)

# Find 
candidates <- html %>% html_elements('[class*="staff-page"], [id*="staff"], [class*="staff"], [class*="team-member"], [class*="staffList"] , [class*="meet_our_staff_wrap"]')

# Select the best candidate node
if (length(candidates) == 0) {
  stop("No candidates found for staff container.")
}

# Count how many staff members each candidate contains
counts <- sapply(candidates, function(node) {
  length(html_elements(node, '[class*="staff"], [class*="staff-card"], [class*="team-member"], [class*="staff-item"], [class*="employee_wrap_staff"]'))
})

best_index <- which.max(counts)
main_staff_node <- candidates[[best_index]]
main_staff_html <- as.character(main_staff_node)

write(main_staff_html, file = output_file)

