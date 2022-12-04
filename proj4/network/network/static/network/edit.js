document.addEventListener("DOMContentLoaded", () => {

    // Handle all edit-buttons
    document.querySelectorAll(".edit-buttons").forEach(button => {
        // Get the Post that is being edited
        const post_id = parseInt(button.dataset.id)
        
        // Add event listener to each button
        button.addEventListener("click", () => {
            console.log(`editButton${post_id} clicked`)
            
            // Disable all other edit-buttons until current edit submitted
            document.querySelectorAll(".edit-buttons").forEach(otherbutton => {
                if (button != otherbutton) {
                    otherbutton.disabled = true
                }
            })
            
            // Fetch Post data and handle editPost view
            fetch(`/posts/edit/${post_id}`, {
                method: "GET"
            })
            .then(response => response.json())
            .then(post => {
                console.log(`Post ${post_id} fetched from database: `, post)
                
                // Hide post view and display edit form
                document.querySelector(`#viewPost${post_id}`).style.display = "none"
                document.querySelector(`#editPost${post_id}`).style.display = "block"
                
                // Pre-fill edit form from database
                document.querySelector(`#editTitle${post_id}`).value = post.title
                document.querySelector(`#editContents${post_id}`).value = post.contents
                
                // Handle submit - call another function
                document.querySelector(`#editPost${post_id}`).onsubmit = () => {
                    // Hide edit form and display new updated post
                    document.querySelector(`#viewPost${post_id}`).style.display = "block"
                    document.querySelector(`#editPost${post_id}`).style.display = "none"
                    
                    // Access form data
                    const title = document.querySelector(`#editTitle${post_id}`).value
                    const contents = document.querySelector(`#editContents${post_id}`).value
                    
                    // Update edited post in database
                    fetch(`/posts/edit/${post_id}`, {
                        method: "POST",
                        body: JSON.stringify({
                            title: title,
                            contents: contents
                        })
                    })
                    .then(response => response.json())
                    .then(data => {
                        console.log("Form submitted, data retrieved: ", data)
                        
                        // Once database updated, update HTML that user sees
                        document.querySelector(`#viewTitle${post_id}`).innerHTML = title
                        document.querySelector(`#viewContents${post_id}`).innerHTML = contents
                        // How to render this directly from model datetimefield without converting manually?
                        document.querySelector(`#viewModified${post_id}`).innerHTML = data.post.modified
                        
                        console.log("Edits to post completed.")
                    })
                    
                    // Enable all other edit-buttons once form submitted
                    document.querySelectorAll(".edit-buttons").forEach(button => {
                        button.disabled = false
                    })
                    
                    // Prevent form from submitting
                    return false;
                }
            })
        })
    })    
})